from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, func



app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

def to_dict(self):
    dictionary ={}
    for column in self.__table__.columns:
        dictionary[column.name]= getattr(self,column.name)
    return dictionary

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search",methods=["GET","POST"])
def search():

    with app.app_context():
        cafe_dict = {}
        cafe_in_area = db.session.execute(db.select(Cafe).where(Cafe.location == request.args.get(key="loc") )).scalars().all()
        if cafe_in_area:
            for cafe in cafe_in_area:
                cafe_dict[f"id {cafe.id}"] = to_dict(cafe)
        else:

            cafe_dict["error"] = {"Not Found":"Sorry, we dont have a cafe at that location."}
        return jsonify(cafe_dict)

@app.route("/all",methods= ["GET"])
def all():
    with app.app_context():
        all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
        print(all_cafes)
        cafe_dict = {}
        for cafe in all_cafes:
            cafe_dict[f"id {cafe.id}"] = to_dict(cafe)
        return jsonify(cafe_dict)

@app.route("/add",methods= ["POST"])
def add():

    with app.app_context():

        cafe_to_add = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(cafe_to_add)
        db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."})
@app.route("/random",methods= ["GET"])
def random():
    with app.app_context():
        random_cafe = db.session.execute(db.select(Cafe).order_by(func.random())).scalar()
        print(random_cafe.name)

    return jsonify(cafe=to_dict(random_cafe))

@app.route("/update-price/<int:cafe_id>",methods=["PATCH"])
def update(cafe_id):

    cafe_to_update = db.get_or_404(Cafe,cafe_id)
    if cafe_to_update:

        cafe_to_update.coffee_price =request.args.get(key="price")
        db.session.commit()
        return jsonify(response={"success": "Price was changed at the new cafe."})
    else:
        return jsonify(response={"error": "Sorry a cafe with that id was not found in the database"})

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    if request.args.get(key='api-key') == 'pog':
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        db.session.delete(cafe_to_update)
        db.session.commit()
        return jsonify(response={"success": "Cafe was dropped"})
    else:
        return jsonify(response={"error": "Sorry, that's not allowed, Make sure you have the correct api_key"}), 403

    #
    #
    # try:
    #     cafe = db.get_or_404(Cafe, id)
    #     new_price = request.args.get('price')
    #     cafe.coffee_price = new_price
    #     db.session.commit()
    #     return jsonify(success='successfully updated the price')
    # except :
    #     return jsonify(error='cafe not found')


@app.errorhandler(404)
def invalid_route(e):
    return jsonify(error={'Not found': 'Sorry a cafe with that id was not found in the database.'}),404
# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
