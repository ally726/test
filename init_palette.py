from app import create_app
from app.models import db, Palette

app = create_app()
with app.app_context():
    db.create_all()
    if not Palette.query.first():
        p = Palette(
            name="Ocean Breeze",
            description="Cool and calm",
            hex_list=["#0E2148", "#483AA0", "#7965C1", "#E3D095"]
        )
        db.session.add(p)
        db.session.commit()
        print("Inserted palette_id =", p.id)
    else:
        print("Palette already exists, id =", Palette.query.first().id)
