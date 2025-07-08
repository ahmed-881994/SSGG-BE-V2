
from app.exceptions.exceptions import ServiceError
from app.schema.entities.createentity import CreateEntityRequest
from app.util.database import connect

entityTypes = {
    1: "teams",
    2: "stages",
    3: "age_groups",
    4: "gender_groups"
}

def create_entity_db(body: CreateEntityRequest):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = []
            args.append(entityTypes.get(body.entity_type))
            args.append(body.entity_name.en)
            args.append(body.entity_name.ar)
            args.append(entityTypes.get(body.entity_type+1))
            cursor.callproc("CreateEntity", args)
            conn.commit()
            entity_record = cursor.fetchone()
            if entity_record is None or entity_record.get("entity_id") is None:
                raise ServiceError(message="Error creating entity", name=None)
            return {"message": f"Entity id {entity_record.get('entity_id')}"}