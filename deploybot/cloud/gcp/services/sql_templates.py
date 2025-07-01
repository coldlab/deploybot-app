POSTGRES_SQL_TEMPLATE = {
    'databaseVersion': 'POSTGRES_14',
    'settings': {
        'tier': 'db-f1-micro',  # Smallest instance for testing
        'backupConfiguration': {
            'enabled': True,
            'binaryLogEnabled': False
        },
        'ipConfiguration': {
            'ipv4Enabled': True,
            'authorizedNetworks': [
                {
                    'name': 'all',
                    'value': '0.0.0.0/0'  # Allow all IPs for testing
                }
            ]
        }
    }
}