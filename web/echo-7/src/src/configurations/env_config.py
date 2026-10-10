from environs import Env


class EnvConfig:
    @staticmethod
    def read():
        env = Env()
        env.read_env()

        return env
