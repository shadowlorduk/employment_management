import tkinter as tk
from tkinter import ttk, messagebox
import pypyodbc as pyodbc  # Use pypyodbc for compatibility with ARM64
import sv_ttk  # Sun Valley theme for ttk
import os  # For environment variables
from dotenv import load_dotenv  # To load environment variables from a .env file
import logging  # For logging to file and console

# Configure logging
logging.basicConfig(
    filename="error_log.txt",  # Log file name
    level=logging.ERROR,  # Log only error-level messages and above
    format="%(asctime)s - %(levelname)s - %(message)s"  # Log format
)

# Load environment variables from a .env file
load_dotenv()


# Connect to the database
def connect_to_db():
    try:
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            f"Encrypt=yes;"  # Encrypt connection)
        )

        return connection
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        messagebox.showerror("Connection Error", f"Error connecting to the database:\n{e}")
        root.quit()  # Stop the application


# Global variable to track data masking state
data_masked = True


# Unified function to display data with optional masking
def display_data(mask_data=True):
    global data_masked  # Use the global variable
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            if mask_data:
                cursor.execute(
                    "SELECT ID, Name, Job_Titles, Department, Full_or_Part_Time, Salary_or_Hourly, Typical_Hours, '****' AS Annual_Salary, '****' AS Hourly_Rate FROM Current_Employee"
                )
                data_masked = True
                column_names = [
                    "ID", "Name", "Job Titles", "Department",
                    "Full/Part-Time", "Salary/Hourly", "Typical Hours",
                    "Annual Salary", "Hourly Rate"
                ]  # Original headings
            else:
                cursor.execute(
                    "SELECT ID, Name, Job_Titles, Department, Full_or_Part_Time, Salary_or_Hourly, Typical_Hours, Annual_Salary, Hourly_Rate FROM Current_Employee")
                data_masked = False
                column_names = [
                    "ID", "Name", "Job Titles", "Department",
                    "Full/Part-Time", "Salary/Hourly", "Typical Hours",
                    "Annual Salary", "Hourly Rate"
                ]  # Original headings (no change needed here, but for clarity)
            rows = cursor.fetchall()
            for row in tree.get_children():
                tree.delete(row)
            for row in rows:
                tree.insert("", tk.END, values=row)

            # Reconfigure column headings
            tree['columns'] = column_names  # Update columns (important if needed)
            for i, col in enumerate(tree['columns']):
                tree.heading(col, text=column_names[i])

        except Exception as e:
            messagebox.showerror("Fetch Error", f"Error fetching data:\n{e}")
        finally:
            connection.close()


# Function to toggle data visibility
def toggle_data_visibility():
    global data_masked

    if data_masked:
        # Require login to reveal sensitive data
        show_login_window()
    else:
        # No login required to hide sensitive data
        display_data(mask_data=True)  # Mask data


# Add data to the database
def add_data():
    if data_masked:
        messagebox.showerror("Operation Error",
                             "Cannot add a record while sensitive data is masked. Please reveal sensitive data first.")
        return

    if not all(
            [name_entry.get(), job_entry.get(), dept_entry.get(), type_entry.get(),
             salary_type_entry.get(), hours_entry.get(), annual_salary_entry.get(),
             hourly_rate_entry.get()]):
        messagebox.showwarning("Input Error", "All fields must be filled out.")
        return

    # Input length checks
    if (len(name_entry.get()) > 50 or
            len(job_entry.get()) > 50 or
            len(dept_entry.get()) > 100 or
            len(type_entry.get()) > 50 or
            len(salary_type_entry.get()) > 50):
        messagebox.showwarning("Input Error", "One or more fields exceed the maximum length.")
        return

    # Validate numeric inputs
    hours_str = hours_entry.get().strip()
    annual_salary_str = annual_salary_entry.get().strip()
    hourly_rate_str = hourly_rate_entry.get().strip()

    if not hours_str:
        messagebox.showwarning("Input Error", "Hours cannot be empty.")
        return
    if not annual_salary_str:
        messagebox.showwarning("Input Error", "Annual Salary cannot be empty.")
        return
    if not hourly_rate_str:
        messagebox.showwarning("Input Error", "Hourly Rate cannot be empty.")
        return

    try:
        typical_hours = int(hours_str) if hours_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error", "Please enter a valid integer value for Hours.")
        return

    try:
        annual_salary = float(annual_salary_str) if annual_salary_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error",
                             "Please enter a valid numeric value for Annual Salary.")
        return

    try:
        hourly_rate = float(hourly_rate_str) if hourly_rate_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error",
                             "Please enter a valid numeric value for Hourly Rate.")
        return

    # Reverse first name and last name and convert to uppercase
    name_parts = name_entry.get().strip().split()
    if len(name_parts) < 2:
        messagebox.showwarning("Input Error", "Please enter both first name and last name.")
        return
    reversed_name = " ".join(name_parts[::-1]).upper()

    # Convert other fields to uppercase
    job_title = job_entry.get().strip().upper()
    department = dept_entry.get().strip().upper()
    full_or_part_time = type_entry.get().strip().upper()

    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """INSERT INTO Current_Employee (Name, Job_Titles, Department, Full_or_Part_Time, Salary_or_Hourly, Typical_Hours, Annual_Salary, Hourly_Rate)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""  # ID removed

            params = (reversed_name, job_title, department, full_or_part_time,
                      salary_type_entry.get(), typical_hours, annual_salary, hourly_rate)
            cursor.execute(query, params)
            connection.commit()
            messagebox.showinfo("Success", "Record added successfully!")
            display_data()  # Refresh data
        except Exception as e:
            logging.error(f"Error adding record: {e}, Query: {query}, Parameters: {params}")
            messagebox.showerror("Insert Error", f"Error adding record:\n{e}")
        finally:
            connection.close()


# Update data in the database
def update_data():
    if data_masked:
        messagebox.showerror("Operation Error",
                             "Cannot update a record while sensitive data is masked. Please reveal sensitive data first.")
        return

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a record to update.")
        return

    if not all(
            [name_entry.get(), job_entry.get(), dept_entry.get(), type_entry.get(),
             salary_type_entry.get(), hours_entry.get(), annual_salary_entry.get(),
             hourly_rate_entry.get()]):
        messagebox.showwarning("Input Error", "All fields must be filled out.")
        return

    # Input length checks
    if (len(name_entry.get()) > 50 or
            len(job_entry.get()) > 50 or
            len(dept_entry.get()) > 100 or
            len(type_entry.get()) > 50 or
            len(salary_type_entry.get()) > 50):
        messagebox.showwarning("Input Error", "One or more fields exceed the maximum length.")
        return

    # Validate numeric inputs
    hours_str = hours_entry.get().strip()
    annual_salary_str = annual_salary_entry.get().strip()
    hourly_rate_str = hourly_rate_entry.get().strip()

    if not hours_str:
        messagebox.showwarning("Input Error", "Hours cannot be empty.")
        return
    if not annual_salary_str:
        messagebox.showwarning("Input Error", "Annual Salary cannot be empty.")
        return
    if not hourly_rate_str:
        messagebox.showwarning("Input Error", "Hourly Rate cannot be empty.")
        return

    try:
        typical_hours = int(hours_str) if hours_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error", "Please enter a valid integer value for Hours.")
        return

    try:
        annual_salary = float(annual_salary_str) if annual_salary_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error",
                             "Please enter a valid numeric value for Annual Salary.")
        return

    try:
        hourly_rate = float(hourly_rate_str) if hourly_rate_str else None
    except ValueError:
        messagebox.showwarning("Data Type Error",
                             "Please enter a valid numeric value for Hourly Rate.")
        return

    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            values = tree.item(selected_item[0], 'values')
            query = """UPDATE Current_Employee
                       SET Name = ?, Job_Titles = ?, Department = ?, Full_or_Part_Time = ?, 
                           Salary_or_Hourly = ?, Typical_Hours = ?, Annual_Salary = ?, Hourly_Rate = ?
                       WHERE ID = ?"""

            params = (name_entry.get(), job_entry.get(), dept_entry.get(),
                      type_entry.get(), salary_type_entry.get(), typical_hours,
                      annual_salary, hourly_rate, values[0])
            cursor.execute(query, params)  # Parameters in a tuple
            connection.commit()
            messagebox.showinfo("Success", "Record updated successfully!")
            display_data(mask_data=False)  # Refresh data without masking
        except Exception as e:
            logging.error(
                f"Error updating record: {e}, Query: {query}, Parameters: {params}, Parameter Types: {[type(p) for p in params]}")
            messagebox.showerror("Update Error", f"Error updating record:\n{e}")
        finally:
            connection.close()


# Delete data from the database
def delete_data():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a record to delete.")
        return

    # Show a confirmation dialog
    confirm = messagebox.askyesno("Confirm Deletion",
                                 "Are you sure you want to delete this record?")
    if not confirm:
        return  # Cancel the deletion if the user selects "No"

    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            values = tree.item(selected_item[0], 'values')
            query = "DELETE FROM Current_Employee WHERE ID = ?"
            cursor.execute(query, (values[0],))
            connection.commit()
            messagebox.showinfo("Success", "Record deleted successfully!")
            display_data()  # Refresh data
        except Exception as e:
            messagebox.showerror("Delete Error", f"Error deleting record:\n{e}")
        finally:
            connection.close()


# Search data in the Treeview
def search_data():
    keyword = search_entry.get().strip().lower()
    for row in tree.get_children():
        tree.delete(row)

    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """SELECT ID, Name, Job_Titles, Department, Full_or_Part_Time, Salary_or_Hourly, 
                       Typical_Hours, Annual_Salary, Hourly_Rate 
                       FROM Current_Employee
                       WHERE LOWER(Name) LIKE ? OR LOWER(Job_Titles) LIKE ? OR LOWER(Department) LIKE ?"""
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching records:\n{e}")
        finally:
            connection.close()


# Populate entry fields for editing
def populate_fields(event):
    selected_item = tree.selection()
    if selected_item:
        values = tree.item(selected_item[0], 'values')
        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])
        job_entry.delete(0, tk.END)
        job_entry.insert(0, values[2])
        dept_entry.delete(0, tk.END)
        dept_entry.insert(0, values[3])
        type_entry.delete(0, tk.END)
        type_entry.insert(0, values[4])
        salary_type_entry.delete(0, tk.END)
        salary_type_entry.insert(0, values[5])
        hours_entry.delete(0, tk.END)
        hours_entry.insert(0, values[6])
        annual_salary_entry.delete(0, tk.END)
        annual_salary_entry.insert(0, values[7])
        hourly_rate_entry.delete(0, tk.END)
        hourly_rate_entry.insert(0, values[8])


# Function to display the login window
def show_login_window():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        # Replace these with your actual credentials
        try:
            valid_username = os.getenv('SEN_USER')
            valid_password = os.getenv('SEN_PASSWORD')
        except Exception as e:  # Catch any exception that may occur
            logging.error(f"Error loading environment variables: {e}")
            messagebox.showerror("Error", "Error loading environment variables.")
            return

        if username == valid_username and password == valid_password:
            login_window.destroy()  # Close the login window
            display_data(mask_data=False)  # Reveal sensitive data
        else:
            # Log incorrect login attempts
            logging.error(f"Incorrect login attempt with username: {username}")
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # Create a new Toplevel window for login
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)

    # Center the login window on the screen
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    window_width = 300
    window_height = 150
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    login_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Username label and entry
    tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10,
                                                 pady=10)
    username_entry = tk.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Password label and entry
    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10,
                                                 pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Login button
    login_button = tk.Button(login_window, text="Login", command=validate_login)
    login_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Bind Enter key to the validate_login function
    login_window.bind('<Return>', lambda event: validate_login())



# Function to display the login window at the start
def show_startup_login(on_success=None):
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        # Replace these with your actual credentials
        try:
            valid_username = os.getenv('SEN_USER')
            valid_password = os.getenv('SEN_PASSWORD')
        except Exception as e:  # Catch any exception that may occur
            logging.error(f"Error loading environment variables: {e}")
            messagebox.showerror("Error", "Error loading environment variables.")
            return

        if username == valid_username and password == valid_password:
            login_window.destroy()  # Close the login window
            root.deiconify()  # Show the main application window
            display_data()  # Initial data display (masked)
        else:
            # Log incorrect login attempts
            logging.error(f"Incorrect login attempt with username: {username}")
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # Create a new Toplevel window for login
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)

    # Hide the main application window until login is successful
    root.withdraw()

    # Disable interaction with the main window until login is successful
    login_window.grab_set()

    # Center the login window on the screen
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    window_width = 300
    window_height = 150
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    login_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Username label and entry
    tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10,
                                                 pady=10)
    username_entry = tk.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Password label and entry
    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10,
                                                 pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Login button
    tk.Button(login_window, text="Login", command=validate_login).grid(row=2,
                                                                     column=0,
                                                                     columnspan=2,
                                                                     pady=10)



# Tkinter GUI
root = tk.Tk()
root.title('Employee Data')  # Set the title of the main window to 'Employee Data'
# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the window width and height
window_width = 800
window_height = 600

# Calculate the position to center the window
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the geometry of the main window
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Call the startup login window
show_startup_login()

# Labels and Entry Widgets
tk.Label(root, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1,
                sticky='ew')  # Make the entry field stretch horizontally

tk.Label(root, text="Job Title:").grid(row=1, column=0)
job_entry = tk.Entry(root)
job_entry.grid(row=1, column=1, sticky='ew')

tk.Label(root, text="Department:").grid(row=2, column=0)
dept_entry = tk.Entry(root)
dept_entry.grid(row=2, column=1, sticky='ew')

tk.Label(root, text="Full/Part-Time:").grid(row=3, column=0)
type_entry = tk.Entry(root)
type_entry.grid(row=3, column=1, sticky='ew')

tk.Label(root, text="Salary/Hourly:").grid(row=4, column=0)
salary_type_entry = tk.Entry(root)
salary_type_entry.grid(row=4, column=1, sticky='ew')

tk.Label(root, text="Typical Hours:").grid(row=5, column=0)
hours_entry = tk.Entry(root)
hours_entry.grid(row=5, column=1, sticky='ew')

tk.Label(root, text="Annual Salary:").grid(row=6, column=0)
annual_salary_entry = tk.Entry(root)
annual_salary_entry.grid(row=6, column=1, sticky='ew')

tk.Label(root, text="Hourly Rate:").grid(row=7, column=0)
hourly_rate_entry = tk.Entry(root)
hourly_rate_entry.grid(row=7, column=1, sticky='ew')

# Search bar
tk.Label(root, text="Search:").grid(row=8, column=0)
search_entry = tk.Entry(root)
search_entry.grid(row=8, column=1,
                sticky='we')  # Search field already stretches horizontally
tk.Button(root, text="Search", command=search_data).grid(row=8, column=2)
tk.Button(root, text="Clear Search", command=display_data).grid(row=8, column=3)

# Configure column 1 to expand horizontally
root.grid_columnconfigure(1, weight=1)

# Treeview to display data
tree = ttk.Treeview(root,
                    columns=('ID', 'Name', 'Job Titles', 'Department',
                             'Full/Part-Time',
                             'Salary/Hourly', 'Typical Hours', 'Annual Salary',
                             'Hourly Rate'), show='headings')
tree.grid(row=10, column=0, columnspan=2, sticky='nsew')

# Configure column headings
for col in tree['columns']:
    tree.heading(col, text=col)

# Add vertical scrollbar for the Treeview
v_scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=v_scrollbar.set)
v_scrollbar.grid(row=10, column=2, sticky='ns')

# Add horizontal scrollbar for the Treeview
h_scrollbar = ttk.Scrollbar(root, orient='horizontal',
                            command=tree.xview)
tree.configure(xscrollcommand=h_scrollbar.set)
h_scrollbar.grid(row=11, column=0, columnspan=2, sticky='ew')

# Adjust grid weights for resizing
root.grid_rowconfigure(10, weight=1)
root.grid_columnconfigure(1, weight=1)

# Buttons
tk.Button(root, text="Add Record", command=add_data).grid(row=9, column=0)
tk.Button(root, text="Update Record", command=update_data).grid(row=9, column=1)
tk.Button(root, text="Delete Record", command=delete_data).grid(row=9, column=2)


# Bind event to populate fields
tree.bind("<Double-1>", populate_fields)

# Initial data display (masked)
display_data()

# Set the theme
sv_ttk.set_theme("light")

# Function to toggle between light and dark themes
def toggle_theme():
    current_theme = sv_ttk.get_theme()
    if current_theme == "light":
        sv_ttk.set_theme("dark")
    else:
        sv_ttk.set_theme("light")

# Create a menu bar
menu_bar = tk.Menu(root)

# Create the "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add "Toggle Theme" option to the "File" menu
file_menu.add_command(label="Toggle Theme", command=toggle_theme)

# Add "Reveal Sensitive Data" option to the "File" menu
file_menu.add_command(label="Reveal Sensitive Data",
                      command=toggle_data_visibility)

# Add an "Exit" option to the "File" menu
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Create the "Help" menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Add "About" option to the "Help" menu
def show_about():
    messagebox.showinfo("About",
                        "Employee Data Manager v1.0\nDeveloped by [Keith Richardson]\n© 2025")


help_menu.add_command(label="About", command=show_about)

# Add "Help" option to the "Help" menu
def show_help():
    messagebox.showinfo("Help",
                        "To use this application:\n\n1. Add, update, or delete employee records.\n2. Use the 'Reveal Sensitive Data' option to view sensitive information.\n3. Use the 'Toggle Theme' option to switch between light and dark themes.")


help_menu.add_command(label="Help", command=show_help)

# Configure the menu bar
root.config(menu=menu_bar)

root.mainloop()  # Start the main event loop