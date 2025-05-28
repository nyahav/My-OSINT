import os

app_name = "MyOSINT"
app_title = "My OSINT API"
app_description = "Open Source Intelligence API"
app_version = "0.1.0"

class Settings:
    DB_TYPE: str = os.getenv("DB_TYPE", "postgres")  
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
   
    DB_PORT: str = os.getenv("DB_PORT", "3306" if DB_TYPE == "mysql" else "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    root_path: str = os.getenv("ROOT_PATH", "")

    @property
    def DATABASE_URL(self):
        """
        Constructs the database connection URL based on DB_TYPE.
        Uses 'mysql+asyncmy' for MySQL and 'postgresql+asyncpg' for PostgreSQL
        to ensure asynchronous driver compatibility.
        """
        if self.DB_TYPE == "mysql":
            return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()