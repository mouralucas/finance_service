import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from services.integration import BcbIntegrationService


class TestBcbIntegrationService:
    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def integration_service(self, mock_session):
        """Create a BcbIntegrationService instance with mocked session."""
        return BcbIntegrationService(mock_session)

    @pytest.mark.asyncio
    async def test_initialization(self, mock_session):
        """Test BcbIntegrationService initialization."""
        service = BcbIntegrationService(mock_session)

        assert service.session == mock_session
        assert "bcdata.sgs" in service.url_bcb
        assert service.core_manager is not None
        assert service.finance_manager is not None

    @pytest.mark.asyncio
    async def test_build_daily_sgs_params_no_latest_date(self, integration_service):
        """Test building daily SGS params when no latest date exists."""
        params = await integration_service._build_daily_sgs_params(
            latest_saved_date=None
        )

        assert "dataInicial=" in params
        assert "dataFinal=" in params
        assert "&" in params

    @pytest.mark.asyncio
    async def test_build_daily_sgs_params_with_latest_date(self, integration_service):
        """Test building daily SGS params with existing latest date."""
        latest_date = datetime.date(2024, 1, 15)

        params = await integration_service._build_daily_sgs_params(
            latest_saved_date=latest_date
        )

        assert "dataInicial=16/01/2024" in params
        assert "dataFinal=" in params

    @pytest.mark.asyncio
    async def test_build_daily_sgs_params_invalid_date(self, integration_service):
        """Test building daily SGS params with future date raises error."""
        future_date = datetime.date.today() + datetime.timedelta(days=10)

        with pytest.raises(ValueError, match="Latest date is already up-to-date"):
            await integration_service._build_daily_sgs_params(
                latest_saved_date=future_date
            )

    @pytest.mark.asyncio
    async def test_build_monthly_sgs_params_no_latest_period(self, integration_service):
        """Test building monthly SGS params when no latest period exists."""
        params = await integration_service._build_monthly_sgs_params(latest_period=None)

        assert "dataInicial=" not in params
        assert "dataFinal=" in params
        assert "dataFinal=" in params

    @pytest.mark.asyncio
    async def test_build_monthly_sgs_params_with_latest_period(
        self, integration_service
    ):
        """Test building monthly SGS params with existing latest period."""
        latest_period = 202401

        params = await integration_service._build_monthly_sgs_params(
            latest_period=latest_period
        )

        assert "dataInicial=" in params
        assert "dataFinal=" in params

    @pytest.mark.asyncio
    async def test_build_monthly_sgs_params_invalid_period_uptodate(
        self, integration_service
    ):
        """Test building monthly SGS params with current period raises error."""
        today = datetime.date.today()
        current_period = today.year * 100 + today.month

        with pytest.raises(ValueError, match="Latest period is already up-to-date"):
            await integration_service._build_monthly_sgs_params(
                latest_period=current_period
            )

    @pytest.mark.asyncio
    async def test_build_monthly_sgs_params_invalid_period_format(
        self, integration_service
    ):
        """Test building monthly SGS params with invalid period format."""
        invalid_period = 202413  # Month 13

        with pytest.raises(ValueError, match="Invalid period format"):
            await integration_service._build_monthly_sgs_params(
                latest_period=invalid_period
            )

    @pytest.mark.asyncio
    async def test_get_from_sgs_success(self, integration_service):
        """Test successful data fetch from SGS API."""
        mock_data = [
            {"data": "01/01/2024", "valor": "100.50"},
            {"data": "02/01/2024", "valor": "101.20"},
        ]

        with patch("services.integration.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response

            mock_client_class.return_value = mock_client

            result = await integration_service._get_from_sgs(
                resource_code=1234, parameters="dataInicial=01/01/2024"
            )

            assert result == mock_data
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_monthly_data_success(self, integration_service, mock_session):
        """Test successful monthly data sync."""
        indexer_id = uuid.uuid4()
        mock_indexer = MagicMock()
        mock_indexer.name = "Test Indexer"

        mock_periodicity_info = {
            "sgs_code": 1234,
            "unit": "%",
        }

        mock_sgs_data = [
            {"data": "01/02/2024", "valor": "100.50"},
        ]

        integration_service.finance_manager.get_indexer_by_id = AsyncMock(
            return_value=mock_indexer
        )
        integration_service.finance_manager.get_indexer_periodicity_info = AsyncMock(
            return_value=mock_periodicity_info
        )
        integration_service.finance_manager.get_latest_finance_series_period = (
            AsyncMock(return_value=202401)
        )
        integration_service._build_monthly_sgs_params = AsyncMock(
            return_value="dataFinal=29/02/2024"
        )
        integration_service._get_from_sgs = AsyncMock(return_value=mock_sgs_data)

        result = await integration_service.sync_monthly_data(indexer_id)

        assert result["successful"] is True
        assert result["quantity"] == 1
        mock_session.add_all.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_monthly_data_no_periodicity_info(
        self, integration_service, mock_session
    ):
        """Test monthly data sync when periodicity info not found."""
        indexer_id = uuid.uuid4()
        mock_indexer = MagicMock()
        mock_indexer.name = "Test Indexer"

        integration_service.finance_manager.get_indexer_by_id = AsyncMock(
            return_value=mock_indexer
        )
        integration_service.finance_manager.get_indexer_periodicity_info = AsyncMock(
            return_value=None
        )

        result = await integration_service.sync_monthly_data(indexer_id)

        assert result["successful"] is False
        assert isinstance(result["exception"], HTTPException)

    @pytest.mark.asyncio
    async def test_sync_daily_data_success(self, integration_service, mock_session):
        """Test successful daily data sync."""
        indexer_id = uuid.uuid4()
        mock_indexer = MagicMock()
        mock_indexer.name = "Test Indexer"

        mock_periodicity_info = {
            "sgs_code": 5678,
            "unit": "base 100",
        }

        mock_sgs_data = [
            {"data": "15/02/2024", "valor": "105.50"},
        ]

        integration_service.finance_manager.get_indexer_by_id = AsyncMock(
            return_value=mock_indexer
        )
        integration_service.finance_manager.get_indexer_periodicity_info = AsyncMock(
            return_value=mock_periodicity_info
        )
        integration_service.finance_manager.get_latest_finance_series_date = AsyncMock(
            return_value=datetime.date(2024, 2, 14)
        )
        integration_service._build_daily_sgs_params = AsyncMock(
            return_value="dataInicial=15/02/2024&dataFinal=16/02/2024"
        )
        integration_service._get_from_sgs = AsyncMock(return_value=mock_sgs_data)

        result = await integration_service.sync_daily_data(indexer_id)

        assert result["successful"] is True
        assert result["quantity"] == 1
        mock_session.add_all.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_daily_data_no_periodicity_info(
        self, integration_service, mock_session
    ):
        """Test daily data sync when periodicity info not found."""
        indexer_id = uuid.uuid4()
        mock_indexer = MagicMock()
        mock_indexer.name = "Test Indexer"

        integration_service.finance_manager.get_indexer_by_id = AsyncMock(
            return_value=mock_indexer
        )
        integration_service.finance_manager.get_indexer_periodicity_info = AsyncMock(
            return_value=None
        )

        result = await integration_service.sync_daily_data(indexer_id)

        assert result["successful"] is False
        assert isinstance(result["exception"], HTTPException)
