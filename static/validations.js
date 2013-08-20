function addCategory(longname, shortname)
{
    var existing_selections = document.getElementById("selected_list").getElementsByTagName("li");
    var existing_number = existing_selections.length;
    
    if (existing_number > 4)
    {
        alert("You have already selected 5 items");
        return;
    }
    
    
    
    var ul = document.getElementById("selected_list");
    var li = document.createElement("li");
    li.id = shortname;

    
    //var div = document.createElement("div");
    //div.className = "category_inner";
    //li.appendChild(div);
    
    
    
    // Fill the new li element with some text that gives the long name, a hidden input field that submits the shortname to the db, and a button that lets the user delete the item
    li.innerHTML = longname;
    //var hidden_field = document.createElement("input");
    //hidden_field.type = "hidden";
    //hidden_field.id = shortname + "_hidden";
    //hidden_field.value = shortname;
    
    //li.appendChild(hidden_field);
    
    var delete_button = document.createElement("input");
    delete_button.type = "button";
    var delete_button_action_name = "";
    delete_button_action_name = delete_button_action_name.concat("delete_", shortname);
    delete_button.value = "Remove";
    delete_button.name = delete_button_action_name;
    delete_button.className = "delete_button";
    
    var helper_arrows = document.createElement("span");
    helper_arrows.className = "ui-icon ui-icon-arrowthick-2-n-s";
    
    li.appendChild(helper_arrows);
    li.appendChild(delete_button);
    
    ul.appendChild(li);
    
    document.getElementsByName(delete_button_action_name)[0].onclick = function () {deleteCategory(shortname); };
    //Disable the button for that stat in the tables so it can't be clicked again
    
    document.getElementsByName(shortname)[0].disabled = true;

    var hidden_value = "";
    
    for (var k = 0; k < existing_number+1; k++){
        hidden_value += document.getElementById("selected_list").getElementsByTagName("li")[k].id.toString();
        hidden_value += ",";
        }
    
    hidden_value = hidden_value.replace(/,+$/, '');
    
    var msg = document.getElementById("selected_msg");
    msg.innerHTML = "Arrange your selections in the order of their importance in the simulation.";
    
    //console.log(hidden_value);
    document.getElementById("selections").value = hidden_value;
    //updateInput();

}

function deleteCategory(shortname) {
    // Delete the li item
    var li = document.getElementById(shortname);
    li.parentNode.removeChild(li);
    
    // Reactivate the button
    document.getElementsByName(shortname)[0].disabled = false;
    
    // Change the message if there are no more categories selected
    var remaining_selections = document.getElementById("selected_list").getElementsByTagName("li").length;
    if (remaining_selections == 0)
    {
        var msg = document.getElementById("selected_msg");
        msg.innerHTML = "No categories selected. The simulator will treat all comparisons equally.";
    }
    
    //Remove the category from the input field
    var hidden_value = "";
    for (var i = 0; i < document.getElementById("selected_list").getElementsByTagName("li").length; i++)
    {
        //console.log(document.getElementById("selected_list").getElementsByTagName("li"));
        var temp_name = document.getElementById("selected_list").getElementsByTagName("li")[i].id.toString();
        if (temp_name == shortname)
        {
            continue;
        }
        hidden_value += temp_name;
        hidden_value += ",";
    }
    hidden_value = hidden_value.replace(/,+$/, '');
    document.getElementById("selections").value = hidden_value;
    //updateInput();
    return; 
}

// jQuery sortable stuff
$( function () {
    $( "#selected_list").sortable({
        update: function( event, ui ) {
            var selections = $( this ).sortable( "toArray" ).toString();
            document.getElementById("selections").value = selections;            
        }
    });
});

function updateInput()
{
    var existing_selections = document.getElementById("selected_list").getElementsByTagName("li");
    console.log(existing_selections);
    var existing_number = existing_selections.length;
    var hidden_value = "";
    
    for (var k = 0; k < existing_number+1; k++){
        hidden_value += document.getElementById("selected_list").getElementsByTagName("li")[k].id.toString();
        hidden_value += ",";
        }
    
    hidden_value = hidden_value.replace(/,+$/, '');
    
    //console.log(hidden_value);
    document.getElementById("selections").value = hidden_value;
}


//Form validation functions

function validatePredictions()
{
    // Get the values
    var away = document.getElementsByName("away")[0].value
    var home = document.getElementsByName("home")[0].value
    // Check that only integers are entered
    
    if (isInteger(home) == false)
    {
        alert("You must enter a whole number for the score");
        return;
    }
    
    if (isInteger(away) == false)
    {
        alert("You must enter a whole number for the score");
        return;
    }
    
    //check that one team is greater than the other
    
    if (home == away)
    {
        alert("You must select a winner")
        return;
    }

    // Check that confidence points are entered
    
    var confidence = document.getElementsByName("confidence")[0].value;
    if (confidence == "-")
    {
        alert("You must select how many confidence points to wager");
        return;
    }
    
    document.getElementById("predictions").submit();
    
}

function isInteger(value)
{
 var temp = parseInt(value);
 
 if (temp == value)
 {
    return true;
 }
 else{
    return false;
 }
}

function loadSimulatorPredictions()
{
    var t = Math.floor((Math.random() * 1500) + 500);
    window.setTimeout(showPredictions, t);
}

function showPredictions()
{
    document.getElementById("enter_predictions").style.visibility = "visible";
    var loading = document.getElementById("loading");
    loading.parentNode.removeChild(loading);
}

