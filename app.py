
import os
import pandas as pd
from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.chat_models import ChatOpenAI

app = Flask(__name__)

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = ''


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_data', methods=['POST'])
def load_data():
    account_number = request.form.get('account_number')
    csv_file = f"{account_number}.csv"
    
    try:
        df = pd.read_csv(csv_file)
        engine = create_engine("sqlite:///creditcard.db")
        df.to_sql("creditcard", engine, index=False, if_exists='replace')
        return jsonify({"message": "Data loaded and saved to SQLite database successfully!"})
    except FileNotFoundError:
        return jsonify({"message": f"Error: The file '{csv_file}' does not exist."}), 400
    except pd.errors.EmptyDataError:
        return jsonify({"message": f"Error: The file '{csv_file}' is empty."}), 400
    except pd.errors.ParserError:
        return jsonify({"message": f"Error: The file '{csv_file}' could not be parsed."}), 400

@app.route('/execute_query', methods=['POST'])
def execute_query():
    sql_query = request.form.get('sql_query')
    
    engine = create_engine("sqlite:///creditcard.db")
    db = SQLDatabase(engine=engine)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    
    result = agent_executor.invoke({"input": sql_query})
    output = result.get("output", "No output returned")
    return output

if __name__ == '__main__':
    app.run(debug=True)
