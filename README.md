# gravy_grocery_store
Flask based grocery store web application.

README - Gravy Flask Web Application Setup

This guide provides step-by-step instructions on how to set up and run this Flask web application. Follow the steps below to get started:

-> Prerequisites
	Before proceeding with the installation, ensure that you have the following prerequisites:

->> Python: Install Python on your system. You can download Python from the official website: python.org.

->> Pip: Install Pip, the package installer for Python. Pip is usually bundled with Python, so you should have it available after installing Python. You can verify its installation by running pip --version in your command prompt or terminal.

->> Code Editor: Install a code editor of your choice. We recommend using Visual Studio Code (VS Code), which can be downloaded from the official website: code.visualstudio.com.

-> Setup Instructions
	Follow these steps to set up and run the Flask web application:

->> Download: Download the project folder and unzip it to your preferred location.

->> Open Project Folder: Open the project folder named 'Code' in your chosen code editor (e.g., VS Code). You should see the project's files and folders within the editor.

->> Terminal Setup: Open a command prompt within your code editor.

->> Install virtualenv: In the command prompt, run the following command to install virtualenv:

pip install virtualenv

->>Create Virtual Environment: After the successful installation of virtualenv, create a virtual environment by running the following command:

virtualenv <name_of_venv>

Replace <name_of_venv> with a suitable name for your virtual environment.

->> Activate Virtual Environment: Navigate to the virtual environment's scripts folder by running the following commands in the command prompt or terminal:

cd <name_of_venv>/Scripts
activate

The virtual environment is now activated, and you should see (venv) in your command prompt or terminal.

->> Return to Code Folder: Move back to the project's code folder by using the following commands in the command prompt or terminal:

cd ../.. OR cd.. (x2)

->> Run the following command to install all the packages required to run this flask applcation.
pip install -r requirement.txt

->> Run the Application: Start the Flask web application by running the following command in the command prompt or terminal:

python app.py

->> Access the Application: Open your preferred web browser and type localhost:5000 in the address bar. The Flask web application should now be running, and you can interact with it.

Congratulations! You have successfully set up and run the Flask web application. Enjoy exploring its features and functionality.

-------------*-------------*--------------*--------------*---------------

If you encounter any issues or have further questions, please contact ktrzorion@gmail.com or 21f1004160@ds.study.iitm.ac.in.

Thank you for using my application!
