// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        uncompleted_tasks:[],
        completed_tasks:[],
        all_tags:[],
        mode:"table",
        selected_task:0,
        task_name:"",
        task_description:"",
        task_deadline:"",
        tag_name:"",
        warning:"",
        form_sub_tag:"",
        form_tag_color:"",
        tag_colors:[],
        selected_tag:null,
        users: [],
        past_selected: [],
        display_asign:""
    };

    // Function to add an _idx field to each element of the array.
    app.enumerate = (a) => {
        let k = 0;
        // Use the map function to iterate over the array and add an _idx field to each element.
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // Get selected users from the users list.
    app.get_selected_users = function(){
        let selected = [];
        // Iterate over the users list and check if the user is selected.
        app.vue.users.forEach(user => {
            if (user.selected) {
                selected.push(user.user.id);
            }
        });
        return selected;
    };
    // Get selected users from the past_selected list.
    app.get_selected_past_users = function(){
        let selected = [];
        // Iterate over the past_selected list and check if the user is selected.
        app.vue.past_selected.forEach(user => {
            if (user.selected) {
                selected.push(user.user.id);
            }
        });
        return selected;
    };

    // Switch the app mode based on the given value.
    app.switch_mode = function(m){
        switch(m){
            case 1:
                app.vue.mode = "table";
                break;
            case 2:
                app.vue.mode = "add";
                break;
            case 3:
                app.vue.mode = "edit"
                break;
            case 4:
                app.vue.mode = "addtag"
                break;
            case 5:
                app.vue.mode = "detail"
                break;
            default:
                app.vue.mode = "table"
        }
    };

    // Show task details in the detail mode.
    app.show_detail = function(task){
        app.vue.selected_task = task.id;
        app.vue.task_name = task.name;
        app.vue.task_description = task.description;
        app.vue.task_deadline = task.deadline;
        app.vue.form_sub_tag = task.tag;
        app.vue.display_asign = task.assigned.join(", ");
        app.switch_mode(5)
    };

    // Switch to edit mode for a specific task.
    app.edit_mode = function(task){
        app.vue.selected_task = task.id;
        app.vue.task_name = task.name;
        app.vue.task_description = task.description;
        app.vue.task_deadline = task.deadline;
        app.vue.form_sub_tag = task.tag;
        app.get_users(task.assigned);
        app.switch_mode(3)
    };

    // Update the task or tag based on the current mode.
    app.update = function(){
        if(app.vue.mode == "edit"){
            // If the mode is "edit", update the task.
            axios.post(edit_url, ({
                task_id: app.vue.selected_task, 
                name: app.vue.task_name, 
                description: app.vue.task_description, 
                deadline: app.vue.task_deadline,
                assigned: [app.get_selected_users(), app.get_selected_past_users()],
                tag:app.vue.form_sub_tag
            })).then(function(respsonse){
                console.log(respsonse);
                // Reset the form fields and selected users.
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];
                // Switch back to the default mode and refresh the tasks.
                app.switch_mode(1);
                app.get_tasks();
            });
        }

        if(app.vue.mode == "add"){
            // If the mode is "add", add a new task.
            // Block the error using warning if required fields are not filled.
            if(app.vue.task_name ===""){
                app.vue.warning = "Type your task name";
                return;
            }
            if(app.vue.task_description === ""){
                app.vue.warning = "Type description";
                return;
            }
            if(app.vue.task_deadline === ""){
                app.vue.warning = "when is the deadline?";
                return;
            }

            app.vue.warning = "";
            
            axios.post(add_url, ({
                name: app.vue.task_name, 
                description: app.vue.task_description, 
                deadline:app.vue.task_deadline,
                assigned: app.get_selected_users(),
                tag:app.vue.form_sub_tag
            })).then(function(respsonse){
                console.log(respsonse);
                // Reset the form fields and selected users.
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];
                // Switch back to the default mode and refresh the tasks.
                app.switch_mode(1);
                app.get_tasks();
            });
        }

        if(app.vue.mode == "addtag"){
            // If the mode is "addtag", add a new tag.
            // Block the error using warning if the tag name is not filled.
            if(app.vue.tag_name ===""){
                app.vue.warning = "Type your tag name";
                return;
            }

            app.vue.warning = "";
            
            axios.post(addtag_url, ({
                name: app.vue.tag_name,
                color: app.vue.form_tag_color})).then(function(response){
                    console.log(response);
                    // Reset the tag name field.
                    app.vue.tag_name = "";
                    // Switch back to the default mode and refresh the tags.
                    app.switch_mode(1);
                    app.get_tags();
                });
        }
    };

    // Get the list of tasks from the server.
    app.get_tasks = function(){
        axios.get(get_tasks_url).then(function(respsonse){
            // Update the uncompleted_tasks and completed_tasks arrays with the retrieved data.
            app.vue.uncompleted_tasks = app.enumerate(respsonse.data.uncompleted);
            app.vue.completed_tasks = app.enumerate(respsonse.data.completed);

            // Iterate over the uncompleted_tasks array and update the timeleft field using Sugar.Date library.
            app.vue.uncompleted_tasks.forEach(task => {
                console.log(task.timeleft);
                task.timeleft = Sugar.Date(task.timeleft).relative().raw;
            });
        });
    };

    // Get the list of tags from the server.
    app.get_tags = function(){
        axios.get(get_tags_url).then(function(response){
            // Update the all_tags array with the retrieved tags data.
            app.vue.all_tags = app.enumerate(response.data.tags);
            console.log("retrieved tags:");
            // Log each tag in the all_tags array.
            app.vue.all_tags.forEach(function(e){
                console.log(e);
            });
        });
    };

    // Get the tag name based on its ID.
    app.tag_name_from_id = function (id){
        let tag_obj = app.vue.all_tags.find(obj => {return obj.id == id});
        if (tag_obj) {
            return tag_obj.name;
        } else {
            return "";
        }
    }

    // Get the tag color based on its ID.
    app.tag_color_from_id = function (id){
        let tag_obj = app.vue.all_tags.find(obj => {return obj.id == id});
        if (tag_obj) {
            // Define a color converter object to map tag colors to corresponding CSS classes.
            let converter = {white: 'is-white', black: 'is-black', red: 'is-danger', green: 'is-success', blue: 'is-link', yellow: 'is-warning', cyan: 'is-info'}
            // Return the corresponding CSS class based on the tag color.
            return converter[tag_obj.color] || 'is-white'
        } else {
            return 'is-white'
        }
    }
  
    // Mark a task as completed.
    app.completed = function(task_id){
        axios.post(complete_task_url, {task_id: task_id}).then(function(respsonse){
            console.log(respsonse);
            // Refresh the list of tasks after marking a task as completed.
            app.get_tasks();
        });
    }

    // Get the list of users from the server.
    app.get_users = function(selected_users=[]) {
        let users = [];
        axios.get(get_users_url).then(function(r) {
            // If there are items in selected users...
            if (selected_users) {
                // if user in selected users...
                r.data.users.forEach(user => {
                    if (selected_users.includes(user.first_name)){
                        users.push({user:user, selected:true}); // mark as true
                    } else {
                        users.push({user:user, selected:false}); // mark as false
                    }
                });
                app.vue.past_selected = JSON.parse(JSON.stringify(users)); // copy
            } else {
                r.data.users.forEach(user => {
                    users.push({user:user, selected:false}); // else just mark all users as false
                });
            }
            app.vue.users = JSON.parse(JSON.stringify(users)); // copy
        });
    };

    // Toggle the selection of a user.
    app.assign_user = function(idx) {
        app.vue.users[idx].selected = !app.vue.users[idx].selected;
    };

    // This contains all the methods.
    app.methods = {
        get_tasks: app.get_tasks,
        completed: app.completed,
        switch_mode: app.switch_mode,
        edit_mode: app.edit_mode,
        get_users: app.get_users,
        assign_user: app.assign_user,
        tag_name_from_id: app.tag_name_from_id,
        tag_color_from_id: app.tag_color_from_id,
        update: app.update,
        show_detail: app.show_detail
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        app.vue.tag_colors = ['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan']
        app.get_tasks();
        app.get_tags();
        app.switch_mode(1);
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
