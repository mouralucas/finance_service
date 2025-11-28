import inspect
from typing import Any

from pydantic import BaseModel, ValidationError


def validate_graphql_input(input_model: type[BaseModel]):
    def decorator(resolver):
        sig = inspect.signature(resolver)
        resolver_params = list(sig.parameters.values())

        async def wrapper(*args, **kwargs):
            func_name = resolver.__name__

            # Ariadne always requires at least (obj, info)
            if len(args) < 2:
                raise ValueError(
                    f"Resolver '{func_name}' must have at least (obj, info)"
                )

            try:
                validation_data = _extract_validation_data(kwargs, input_model)
                validated_input = input_model.model_validate(validation_data)

                target_param = _find_target_param(resolver_params, input_model)

                if target_param:
                    # Inject only the validated object
                    new_kwargs = {target_param: validated_input}
                else:
                    # Inject all model fields as kwargs
                    new_kwargs = validated_input.model_dump()

                try:
                    bound = sig.bind(*args, **new_kwargs)
                except TypeError as e:
                    raise TypeError(
                        f"Error binding parameters for resolver '{func_name}': {e}"
                    )

                return await resolver(*bound.args, **bound.kwargs)

            except ValidationError as ve:
                raise Exception(
                    f"Input validation error in resolver '{func_name}': {ve}"
                ) from ve

        return wrapper

    return decorator


def _extract_validation_data(kwargs: dict[str, Any], input_model: type[BaseModel]):
    """
    Extract the dictionary that corresponds to the input model.

    Handles cases:
    - resolver(arg={...})
    - resolver(input={...})
    - resolver(params={...})
    - resolver(input={params:{...}})
    """

    model_fields = set(input_model.model_fields.keys())

    # 1. Direct match: some kwarg matches model fields
    if model_fields.intersection(kwargs.keys()):
        return kwargs

    # 2. Single dict in kwargs → assume it's the payload
    dict_values = [v for v in kwargs.values() if isinstance(v, dict)]
    if len(dict_values) == 1:
        return dict_values[0]

    # 3. Nested dict -> search for first matching dict
    for key, value in kwargs.items():
        if isinstance(value, dict) and model_fields.intersection(value.keys()):
            return value

    # Fallback: return kwargs as-is (may fail validation)
    return kwargs


def _find_target_param(params, input_model: type[BaseModel]) -> str | None:
    """
    Identify the resolver parameter that should receive the validated model.
    """

    model_name = input_model.__name__.lower().replace("input", "")

    # Skip obj and info
    relevant = params[2:]

    for param in relevant:
        name = param.name.lower()

        if model_name in name or "input" in name or "validated" in name:
            return param.name

    # If there is exactly one parameter after obj/info, assume it's the input
    if len(relevant) == 1:
        return relevant[0].name

    return None
