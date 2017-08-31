
/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction(id) {
    document.getElementById(id).classList.toggle("show");
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {

        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

var Password = {

    _pattern : /[a-zA-Z0-9]/,

    _getRandomByte : function() {
        if(window.crypto && window.crypto.getRandomValues)
        {
            var result = new Uint8Array(1);
            window.crypto.getRandomValues(result);
            return result[0];
        }
        else if(window.msCrypto && window.msCrypto.getRandomValues)
        {
            var result = new Uint8Array(1);
            window.msCrypto.getRandomValues(result);
            return result[0];
        }
        else
        {
            return Math.floor(Math.random() * 256);
        }
    },

    generate : function(length) {
        return Array.apply(null, {'length': length})
            .map(function()
            {
                var result;
                while(true)
                {
                    result = String.fromCharCode(this._getRandomByte());
                    if(this._pattern.test(result))
                    {
                        return result;
                    }
                }
            }, this)
            .join('');
    },

    new_password : function() {
        var new_pw = this.generate(16);
        document.getElementById("id_password").value = new_pw;
        document.getElementById("password_display").innerHTML = new_pw;
    }


};