from flask import Flask, request, jsonify,g
from db.conexion import conect, create_tables, connect_db
from datetime import datetime

app = Flask(__name__)

# Crear las tablas al inicio de la aplicación
def create_database_tables():
    conn = conect()
    create_tables(conn)
    conn.close()

# Rutas y funciones de vista
@app.route('/tasks', methods=['GET'])
@connect_db
def tasks():
    cursor = g.conn.cursor()
    try:
        # Ejecutar la consulta SQL para obtener todas las tareas
        cursor.execute("SELECT * FROM tasks")
        tareas = cursor.fetchall()

        # Crear una lista de diccionarios para almacenar los resultados
        tareas_list = []
        for tarea in tareas:
            tarea_dict = {
                'id': tarea[0],
                'title': tarea[1],
                'description': tarea[2],
                'status': tarea[3],
                'due_date': tarea[4],
                'user_id': tarea[5],
                'crate_date': tarea[6]
            }
            tareas_list.append(tarea_dict)

        return jsonify(tareas_list), 200

    except Exception as e:
        return jsonify({'mensaje': f'Error al obtener las tareas: {str(e)}'}), 500

@app.route('/add_task', methods=['POST'])
@connect_db
def add_task():
    # Obtener los datos de la solicitud POST
    data = request.json
    
    try:
        tasks = data['tasks']

        # Conectar a la base de datos
        cursor = g.conn.cursor()

        # Iterar sobre la lista de tareas y agregarlas a la base de datos
        for task in tasks:
            titulo = task.get('titulo')
            descripcion = task.get('descripcion')
            estado = task.get('estado')
            fecha_vencimiento = task.get('fecha_vencimiento')
            user_id = task.get('user_id')
            
            # Obtener fecha del sistema
            create_date = datetime.now()

            # Validar que se hayan proporcionado todos los datos necesarios
            if not (titulo and estado and fecha_vencimiento and user_id):
                return jsonify({'mensaje': 'Se requieren el título, estado, fecha de vencimiento y user_id'}), 400
            
            # Ejecutar la consulta SQL para insertar la tarea en la base de datos
            cursor.execute("INSERT INTO tasks (title, description, status, due_date, user_id, crate_date) VALUES (%s, %s, %s, %s, %s, %s)",
                            (titulo, descripcion, estado, fecha_vencimiento, user_id, create_date,))
        
        return jsonify({'mensaje': 'Tarea creada correctamente.'}), 201

    except Exception as e:
        return jsonify({'mensaje': f'Error al crear la tarea: {str(e)}'}), 500

@app.route('/edit_task/<int:id_task>', methods=['PUT'])
@connect_db
def edit_task(id_task):
    # Lógica para actualizar tarea
    datos = request.json
    titulo = datos.get('titulo')
    descripcion = datos.get('descripcion')
    estado = datos.get('estado')
    fecha_vencimiento = datos.get('fecha_vencimiento')
    
    #conexion a base de datos
    cursor = g.conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id_task = %s", (id_task,))
    tarea_actual = cursor.fetchone()

    # Verificar y actualizar los campos solo si no están vacíos en la solicitud
    if titulo is None:
        titulo = tarea_actual[1]  # Mantener el valor actual del título
    if descripcion is None:
        descripcion = tarea_actual[2]  # Mantener el valor actual de la descripción
    if estado is None:
        estado = tarea_actual[3]  # Mantener el valor actual del estado
    if fecha_vencimiento is None:
        fecha_vencimiento = tarea_actual[4]  # Mantener el valor actual de la fecha de vencimiento

    
    try:
        cursor.execute("""
                       UPDATE tasks
                       SET title= %s,description = %s,status = %s,due_date = %s
                       WHERE id_task =%s
                       """,(titulo,descripcion,estado,fecha_vencimiento,id_task))

        return jsonify({'mensaje': 'Tarea actualizada correctamente.'}), 200
    except Exception as e:
        return jsonify({'mensaje':f'Error al editar la tarea:{str(e)}'}), 500

@app.route('/delete_task/<int:id>', methods=['DELETE'])
@connect_db
def delete_task(id):
    try:
        # Conectar a la base de datos
        cursor = g.conn.cursor()

        # Ejecutar la consulta SQL para eliminar la tarea con el ID proporcionado
        cursor.execute("DELETE FROM tasks WHERE id_task = %s", (id,))

        return jsonify({'mensaje': f'Tarea con ID {id} eliminada correctamente.'}), 200

    except Exception as e:
        return jsonify({'mensaje': f'Error al eliminar la tarea: {str(e)}'}), 500


# Ruta para buscar una tarea por su ID
@app.route('/search_task/<int:id>', methods=['GET'])
@connect_db
def search_task(id):
    try:
        # Conectar a la base de datos
        cursor = g.conn.cursor()

        # Ejecutar la consulta SQL para buscar la tarea con el ID proporcionado
        cursor.execute("SELECT * FROM tasks WHERE id_task = %s", (id,))
        task = cursor.fetchone()

        if task:
            task_data = {
                'id_task': task[0],
                'title': task[1],
                'description': task[2],
                'status': task[3],
                'due_date': task[4],
                'user_id': task[5],
                'create_date': task[6]
            }
            return jsonify(task_data), 200
        else:
            return jsonify({'mensaje': f'No se encontró la tarea con el ID {id}'}), 404

    except Exception as e:
        return jsonify({'mensaje': f'Error al buscar la tarea: {str(e)}'}), 500
    
if __name__ == '__main__':
    
    create_database_tables()
    app.run(debug=True)
