from model import Database, Activity, Product, BiosphereExchange, TechnosphereExchange, ExchangeType


def parse(d: dict) -> Database:
    (database_name, database_version), activity_dicts = list(d.items())[0]

    activities: list[Activity] = []
    for activity_dict in activity_dicts:
        products: list[Product] = []
        biosphere: list[BiosphereExchange] = []
        technosphere: list[TechnosphereExchange] = []
        for exchange in activity_dict['exchanges']:
            exchange_name, quantity = exchange['name'], exchange['quantity']

            match exchange_type := ExchangeType(exchange['type']):
                case ExchangeType.PRODUCTION:
                    products.append(Product(exchange_name, quantity, exchange['allocation']))
                case ExchangeType.TECHNOSPHERE:
                    technosphere.append(TechnosphereExchange(exchange_name, quantity))
                case ExchangeType.BIOSPHERE | ExchangeType.EMISSION:
                    biosphere.append(BiosphereExchange(exchange_name, quantity, ExchangeType(exchange_type)))

        activities.append(Activity(activity_dict['name'], products, biosphere, technosphere))

    return Database(database_name, database_version, activities)
