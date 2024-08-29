from models.core import CountryModel, TaxModel


def get_mocked_countries() -> list[CountryModel]:
    country_list: list[CountryModel] = []

    brazil = CountryModel(id='BR', name='Brasil')
    united_states = CountryModel(id='US', name='Estados Unidos da América')
    germany = CountryModel(id='DE', name='Germany')
    australia = CountryModel(id='AU', name='Australia')

    country_list.append(brazil)
    country_list.append(united_states)
    country_list.append(germany)
    country_list.append(australia)

    return country_list


def get_mocked_tax():
    tax_list: list[TaxModel] = []
    country_list = get_mocked_countries()

    ir = TaxModel(name='Imposto de Renda', acronyms='IR', description='Imposto sobre a renda', country=country_list[0])
    iof = TaxModel(name='Imposto sobre Operações Financeiras', acronyms='IOF', description='Imposto sobre as operações financeiras', country=country_list[0])

    tax_list.append(ir)
    tax_list.append(iof)

    return tax_list