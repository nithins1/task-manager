# task-manager



# Description (200 words)
A web application where you can enter tasks that you need to do and when they need to be completed by. The site will display which of your tasks are currently incomplete, and you can mark them as complete by clicking a button. You can also view previously completed tasks and mark them as incomplete to reactivate them.

# Main Pages
index: List of all active tasks and their deadlines. For each task there is a "mark as complete" button. There is also a button to go to the "history" and "add" pages.

add: Form where you can submit a task name, description, and deadline.

history: Page where you can view a list of old tasks. Each one has a button to "mark as incomplete".

All of the logic will be server-side. No frontend code will be needed, except for fancy cosmetic effects if we have time.

# Data Organization
tasks: Table that keeps track of each task's name, description, user, deadline, and completion status. Tasks on the index page will only be displayed if they have false for is_completed. Tasks will also be sorted by their deadlines. Also each user can only see their own tasks.

images: If we have time, we could have some images associated with each task. The user submits images on the add page, and on the index page they are displayed along with the task.

users: Standard py4web auth table from scaffold.

# User Stories
A user creates an account and is redirected to the index page, which has no tasks displayed currently. They click the "add task" button and go to the add page. They enter the task name, description, and date/time it needs to be completed by. After submitting the form, they are redirected to the index page, which now displays the task. They repeat this multiple times for each of their tasks. Now, the user goes and starts completing their tasks, and marks each task as complete whenever appropriate. The completed tasks disappear from the index page. When the user realizes that a task they previously completed is actually not done and needs to be reactivated, they go to the history page and marks that task as incomplete, so it reappears on the index page.

# Implementation Plan
Sprint 1: Database setup, index page shows tasks, add page inserts new tasks, appropriate buttons on index page for marking tasks as complete and adding tasks
Sprint 2: History page shows old tasks, index page has history button, history page has buttons for reactivating tasks
Sprint 3: Stylistic cleanup, and implement images for tasks. Image files will be stored in Google Cloud Storage and the images table will have a row for each image and which task it is associated with. Index page shows images for each task.

