
class ServiceLocator:
    _services = {}

    @classmethod
    def add_service(cls, name, service):
        cls._services[name] = service

    @classmethod
    def get_service(cls, name):
        return cls._services.get(name)
   
   