# Shristi AI Integration

This project is the current Dekho Bharat Django project with the supplied Shristi chatbot integrated into the existing `chatbot` app.

## Active module
`/shristi/`

## API endpoints
- `/shristi/api/`
- `/shristi/places/`
- `/shristi/place/<place-name>/`

## Notes
- Existing GoPlan/Django modules were kept as the base project.
- Shristi's richer `engine.py`, local image library, and frontend were integrated.
- The existing shared GoPlan sidebar is used instead of a duplicate Shristi sidebar.
- Shristi place image assets are served from `/static/chatbot/places/...`.
