try:
    # Import libraries
    from flights_searcher import search_flights                         # Function for API request
    from datetime import timedelta, datetime
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator        # Python operator to execute functions 
    from airflow.operators.email_operator import EmailOperator          # Email operator to send email
    from airflow.operators.python_operator import BranchPythonOperator  # Branch operator to check conditions
    from airflow.operators.dummy_operator import DummyOperator          # Dummy operator to do nothing when condition fail
    from airflow.models.variable import Variable                        # Function to get environmental variables from airflow

    # Setting up Triggers
    from airflow.utils.trigger_rule import TriggerRule

    print("All Dag modules are ok ......")

except Exception as e:
    print("Error  {} ".format(e))



#-------------------------------------------------------------------------
THRESHOLD = 8000  # MXN threshold value to consider a round flight as cheap  
#-------------------------------------------------------------------------


# Function to evaluate flight prices
def evaluate_flight_prices(**context):
    ti = context['ti']
    flights_data = ti.xcom_pull(task_ids='Search_flights')
    for index, flight in flights_data.iterrows():
        if flight['Price_mxn'] <= THRESHOLD:
            return 'Send_email'
    return 'Do_nothing'

# Function to call when DAG fails
def on_failure_callback(context):
    '''Function to execute in case there is an error during DAG running'''

    print("Fail works  !  ")


# DAG definition
with DAG(dag_id="Flight_search",
         schedule_interval="@once",                         # How frequently the DAG is going to run
         default_args={
             "owner": "airflow",
             "start_date": datetime(2024, 4, 10),           # First date of execution
             "retries": 1,
             "retry_delay": timedelta(minutes=1),           # How much time must pass to re-run after failure
             'on_failure_callback': on_failure_callback,
             'email': ['jc.barreras.maldonado@gmail.com'],  
             'email_on_failure': False,
             'email_on_retry': False,
         },
         catchup=False) as dag:

    # DAG to request API flights information
    search_flights_task = PythonOperator(
        task_id='Search_flights',
        python_callable=search_flights,
        provide_context=True,  # Needed if context is required for the function to work
        op_kwargs={'origin': 'HMO', 'destination': 'MEX', 'api_token': Variable.get("API_FLIGHTS_SECRET_TOKEN")}  # Provide search_flights() arguments
    )

    # DAG to evaluate flight prices and decide whether to send email or not
    evaluate_flight_prices_task = BranchPythonOperator(
        task_id='Evaluate_flight_prices',
        python_callable=evaluate_flight_prices,
        provide_context=True,
    )


    # DAG to send email if a cheap flight is found
    send_email_task = EmailOperator(
        task_id='Send_email',
        to='jc.barreras.maldonado@gmail.com',
        subject='Airflow Alert: Vuelos Baratos Encontrados',
        #provide_context=True,  # Indicar a Airflow que proporcione el contexto
        html_content=""" 
        <h3>Se han encontrado vuelos baratos!</h3> 
        <p>A continuación se muestra la información de los vuelos:</p>
        <table border="1">
            <tr>
                <th>Origen</th>
                <th>Destino</th>
                <th>Número de vuelo</th>
                <th>Aerolínea</th>
                <th>Fecha de salida</th>
                <th>Hora de salida</th>
                <th>Fecha de regreso</th>
                <th>Hora de regreso</th>
                <th>Precio (MXN)</th>
                <th>Fecha de expiración del precio (UTC+0)</th>
            </tr>
            {% for index, flight in task_instance.xcom_pull(task_ids='Search_flights').iterrows() %}
            <tr>
                <td>{{ flight['Origin'] }}</td>
                <td>{{ flight['Destination'] }}</td>
                <td>{{ flight['Flight_number'] }}</td>
                <td>{{ flight['Airline'] }}</td>
                <td>{{ flight['Departure_date'] }}</td>
                <td>{{ flight['Departure_times'] }}</td>
                <td>{{ flight['Return_date'] }}</td>
                <td>{{ flight['Return_times'] }}</td>
                <td>{{ flight['Price_mxn'] }}</td>
                <td>{{ flight['Price_expiration_UTC+0'] }}</td>
            </tr>
            {% endfor %}
        </table>
        """,
    )

    # Define la tarea Do_nothing
    do_nothing_task = DummyOperator(
        task_id='Do_nothing'
    )

    # Define dependencias entre tareas
    search_flights_task >> evaluate_flight_prices_task
    evaluate_flight_prices_task >> [send_email_task, do_nothing_task]
