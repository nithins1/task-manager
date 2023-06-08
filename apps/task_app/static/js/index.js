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
        past_selected: []
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.get_selected_users = function(){
        let selected = [];
        app.vue.users.forEach(user => {
            if (user.selected) {
                selected.push(user.user.id);
            }
        });
        return selected;
    };
    app.get_selected_past_users = function(){
        let selected = [];
        app.vue.past_selected.forEach(user => {
            if (user.selected) {
                selected.push(user.user.id);
            }
        });
        return selected;
    };


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
            default:
                app.vue.mode = "table"
        }
    };

    app.edit_mode = function(task){
        app.vue.selected_task = task.id;
        app.vue.task_name = task.name;
        app.vue.task_description = task.description;
        app.vue.task_deadline = task.deadline;
        app.vue.form_sub_tag = task.tag;
        app.get_users(task.assigned);
        app.switch_mode(3)
    };

    app.update = function(){
        if(app.vue.mode == "edit"){
            axios.post(edit_url, ({
                task_id: app.vue.selected_task, 
                name: app.vue.task_name, 
                description: app.vue.task_description, 
                deadline: app.vue.task_deadline,
                assigned: [app.get_selected_users(), app.get_selected_past_users()],
                tag:app.vue.form_sub_tag
            })).then(function(respsonse){
                console.log(respsonse);
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];

                app.switch_mode(1);
                app.get_tasks();
            });
        }

        if(app.vue.mode == "add"){
            //Block the error using warning
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
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];

                app.switch_mode(1);
                app.get_tasks();
            });
        }

        if(app.vue.mode == "addtag"){
            //Block the error using warning
            if(app.vue.tag_name ===""){
                app.vue.warning = "Type your tag name";
                return;
            }

            app.vue.warning = "";
            
            axios.post(addtag_url, ({
                name: app.vue.tag_name,
                color: app.vue.form_tag_color})).then(function(response){
                    console.log(response);
                    app.vue.tag_name = "";

                    app.switch_mode(1);
                    app.get_tags();
                });
        }
    };

    app.get_tasks = function(){
        axios.get(get_tasks_url).then(function(respsonse){
            app.vue.uncompleted_tasks = app.enumerate(respsonse.data.uncompleted);
            app.vue.completed_tasks = app.enumerate(respsonse.data.completed);
        });
    };

    app.get_tags = function(){
        axios.get(get_tags_url).then(function(response){
            app.vue.all_tags = app.enumerate(response.data.tags);
            console.log("retrieved tags:");
            app.vue.all_tags.forEach(function(e){
                console.log(e);
            });
        });
    };

    app.tag_name_from_id = function (id){
        let tag_obj = app.vue.all_tags.find(obj => {return obj.id == id});
        if (tag_obj) {
            return tag_obj.name;
        } else {
            return "";
        }
    }

    app.tag_color_from_id = function (id){
        let tag_obj = app.vue.all_tags.find(obj => {return obj.id == id});
        if (tag_obj) {
            let converter = {white: 'is-white', black: 'is-black', red: 'is-danger', green: 'is-success', blue: 'is-link', yellow: 'is-warning', cyan: 'is-info'}
            return converter[tag_obj.color] || 'is-white'
        } else {
            return 'is-white'
        }
    }
    app.completed = function(task_id){
        axios.post(complete_task_url, {task_id: task_id}).then(function(respsonse){
            console.log(respsonse);
            app.get_tasks();
        });
    }

    app.get_users = function(selected_users=[]) {
        let users = [];
        axios.get(get_users_url).then(function(r) {
            //app.vue.users = r.data.users;
            if (selected_users) {
                r.data.users.forEach(user => {
                    if (selected_users.includes(user.first_name)){
                        users.push({user:user, selected:true});
                    } else {
                        users.push({user:user, selected:false});
                    }
                });
                app.vue.past_selected = JSON.parse(JSON.stringify(users));
            } else {
                r.data.users.forEach(user => {
                    users.push({user:user, selected:false});
                });
            }
            app.vue.users = JSON.parse(JSON.stringify(users));
        });
    };

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
        update: app.update
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
