import platform


class ServiceUtils:
    def __init__(self) -> None:
        if platform.system() != "Windows":
            # production
            static_path = "/root/icecreamapi-app/icecreamapi/static/"
        else:
            # local development on windows
            static_path = "C:\\Users\\Vitaly\\Desktop\\static\\"
        self.static_path = static_path

    def get_static_path(self):
        return self.static_path
