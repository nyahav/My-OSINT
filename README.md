# 🕵️‍♂️ The OSINT Web Application

**The OSINT Web Application** is a web-based platform for collecting and analyzing open-source intelligence (OSINT) from publicly available online sources.  
It provides user management, secure authentication, smart data queries, and an interactive, modern interface.

---

## 📸 Screenshot
![Screenshot of the app](images/OSINT-screenshot.png)

---

## ⚙️ Tech Stack

## ⚛️ Frontend Stack

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Technologies</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🌐 Framework</td>
      <td>
        <a href="https://reactjs.org/">
          <img src="https://img.shields.io/badge/React-%2320232A.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" alt="React" />
        </a>
      </td>
    </tr>
    <tr>
      <td>🎨 Styling</td>
      <td>
        <a href="https://tailwindcss.com/">
          <img src="https://img.shields.io/badge/Tailwind%20CSS-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
        </a>
      </td>
    </tr>
    <tr>
      <td>💻 Languages</td>
      <td>
        <a href="https://www.typescriptlang.org/">
          <img src="https://img.shields.io/badge/TypeScript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
        </a>
        <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript">
          <img src="https://img.shields.io/badge/JavaScript-%23F7DF1E.svg?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
        </a>
      </td>
    </tr>
  </tbody>
</table>

---

## 🧠 Backend Stack

<table>
  <thead>
    <tr>
      <th>Tool</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <a href="https://fastapi.tiangolo.com/">
          <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
        </a>
      </td>
      <td>A modern, fast web framework based on Python type hints.</td>
    </tr>
    <tr>
      <td>
        <a href="https://www.uvicorn.org/">
          <img src="https://img.shields.io/badge/Uvicorn-333333?style=for-the-badge&logo=uvicorn&logoColor=white" alt="Uvicorn" />
        </a>
      </td>
      <td>High-performance ASGI server to run FastAPI.</td>
    </tr>
    <tr>
      <td>
        <a href="https://docs.pydantic.dev/">
          <img src="https://img.shields.io/badge/Pydantic-0F172A?style=for-the-badge&logo=python&logoColor=white" alt="Pydantic" />
        </a>
      </td>
      <td>Data validation and parsing using Python typing.</td>
    </tr>
    <tr>
      <td>
        <a href="https://www.sqlalchemy.org/">
          <img src="https://img.shields.io/badge/SQLAlchemy-CA4245?style=for-the-badge&logo=python&logoColor=white" alt="SQLAlchemy" />
        </a>
      </td>
      <td>ORM for database interaction.</td>
    </tr>
    <tr>
      <td>
        <a href="https://pypi.org/project/psycopg2-binary/">
          <img src="https://img.shields.io/badge/psycopg2--binary-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="psycopg2-binary" />
        </a>
      </td>
      <td>PostgreSQL database driver.</td>
    </tr>
    <tr>
      <td>
        <a href="https://github.com/mpdavis/python-jose">
          <img src="https://img.shields.io/badge/python--jose-363636?style=for-the-badge&logo=python&logoColor=white" alt="python-jose" />
        </a>
      </td>
      <td>JWT-based authentication handling.</td>
    </tr>
    <tr>
      <td>
        <a href="https://passlib.readthedocs.io/">
          <img src="https://img.shields.io/badge/passlib-bcrypt-%23007ACC?style=for-the-badge&logo=python&logoColor=white" alt="passlib" />
        </a>
      </td>
      <td>Secure password hashing.</td>
    </tr>
    <tr>
      <td>
        <a href="https://saurabh-kumar.com/python-dotenv/">
          <img src="https://img.shields.io/badge/python--dotenv-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="python-dotenv" />
        </a>
      </td>
      <td>Loads environment variables from a <code>.env</code> file.</td>
    </tr>
    <tr>
      <td>
        <a href="https://alembic.sqlalchemy.org/">
          <img src="https://img.shields.io/badge/Alembic-CA4245?style=for-the-badge&logo=python&logoColor=white" alt="Alembic" />
        </a>
      </td>
      <td>Manages database schema migrations.</td>
    </tr>
    <tr>
      <td>
        <a href="https://docs.pytest.org/">
          <img src="https://img.shields.io/badge/pytest-0A0A0A?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest" />
        </a>
      </td>
      <td>Unit and integration testing framework.</td>
    </tr>
  </tbody>
</table>


---

## 🚀 Getting Started

### Registration
Sign up via the app's registration form using:
- Username
- Email
- Password

### Running the Application-Three-command quick-start

```bash
git clone https://github.com/nyahav/My-OSINT.git 
(cd My-OSINT)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build 
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
