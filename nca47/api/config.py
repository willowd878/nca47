# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'nca47.api.controllers.root.RootController',
    'modules': ['nca47'],
    'debug': False
}
