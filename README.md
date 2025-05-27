# 🕵️‍♂️ The OSINT Web Application

**The OSINT Web Application** is a web-based platform for collecting and analyzing open-source intelligence (OSINT) from publicly available online sources.  
It provides user management, secure authentication, smart data queries, and an interactive, modern interface.

---

## 📸 Screenshot
> 🖼️ A screenshot of the application will appear here

---

## ⚙️ Tech Stack

<table>
    <thead>
        <tr>
            <th>Property</th>
            <th>Badges</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>🎨 Design</td>
            <td>
                <a href="https://www.framer.com/motion/">
                    <img src="https://img.shields.io/badge/Framer%20Motion-%23EF4B4A.svg?style=for-the-badge&logo=framer&logoColor=white" alt="Framer Motion">
                </a>
                <a href="https://tailwindcss.com/">
                    <img src="https://img.shields.io/badge/Tailwind%20CSS-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
                </a>
            </td>
        </tr>
        <tr>
            <td>📋 Languages & Tools</td>
            <td>
                <a href="https://www.typescriptlang.org/">
                    <img src="https://img.shields.io/badge/TypeScript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
                </a>
                <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript">
                    <img src="https://img.shields.io/badge/JavaScript-%23F7DF1E.svg?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
                </a>
            </td>
        </tr>
        <tr>
            <td>📚 Libraries</td>
            <td>
                <a href="https://threejs.org/">
                    <img src="https://img.shields.io/badge/Three.js-%23000000.svg?style=for-the-badge&logo=three.js&logoColor=white" alt="Three.js">
                </a>
                <a href="https://reactjs.org/">
                    <img src="https://img.shields.io/badge/React-%2320232A.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" alt="React">
                </a>
            </td>
        </tr>
        <tr>
            <td>🚀 Frameworks</td>
            <td>
                <a href="https://nextjs.org/">
                    <img src="https://img.shields.io/badge/Next.js-%23000000.svg?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js">
                </a>
            </td>
        </tr>
        <tr>
            <td>📦 Features</td>
            <td>
                <a href="https://threejs.org/">
                    <img src="https://img.shields.io/badge/3D%20Interactive%20Elements-%23000000.svg?style=for-the-badge&logo=three.js&logoColor=white" alt="3D Interactive Elements">
                </a>
                <a href="https://framer.com/motion/">
                    <img src="https://img.shields.io/badge/Animations-%23EF4B4A.svg?style=for-the-badge&logo=framer&logoColor=white" alt="Framer Motion Animations">
                </a>
            </td>
        </tr>
    </tbody>
</table>

---

## 🧠 Backend Stack

- **FastAPI** – A modern, fast web framework based on Python type hints.
- **Uvicorn[standard]** – A high-performance ASGI server to run FastAPI.
- **Pydantic** – For data validation and parsing using Python typing.
- **SQLAlchemy** – A powerful ORM for database interaction.
- **psycopg2-binary** – PostgreSQL database driver (can be replaced based on your DB).
    - For **SQLite**: No additional driver is needed (or `aiosqlite` for async support).
    - For **MySQL**: Use `mysqlclient`.
- **python-jose[cryptography]** – For handling JWT-based authentication.
- **passlib[bcrypt]** – For secure password hashing.
- **python-dotenv** – Loads environment variables from a `.env` file.
- **Alembic** – For managing database schema migrations.
- **pytest** – For writing and running unit/integration tests.

---

## 🚀 Getting Started

### Registration
Sign up via the app's registration form using:
- Username
- Email
- Password

### Running the Application

```bash
docker-compose up --build
