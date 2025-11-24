call venv\Scripts\activate

REM start cmd /k "npx tailwindcss -i ./static/styles/input.css -o ./static/styles/output.css --watch"

flask --app app run --debug