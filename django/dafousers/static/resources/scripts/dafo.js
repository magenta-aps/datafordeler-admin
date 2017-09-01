var DAFO = window.DAFO || {};

(function($, w, DAFO) {

    // Close the dropdown if the user clicks outside of it
    w.onclick = function(event) {
        if (event.target.closest('.dropbtn') === null) {

            var dropdowns = document.getElementsByClassName("dropdown-content");
            var i;
            for (i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
        if (event.target.id === "lightbox") {
            event.target.classList.add('hidden');

            var popups = document.getElementsByClassName("popup");

            for (i = 0; i < popups.length; i++) {
                var openPopup = popups[i];
                if (!openPopup.classList.contains('hidden')) {
                    openPopup.classList.add('hidden');
                }
            }
        }
    };

    /* When the user clicks on the button,
    toggle between hiding and showing the dropdown content */
    w.toggleShow = function(id) {
        document.getElementById(id).classList.toggle("show");
    };

    w.toggleHidden = function(id) {
        document.getElementById(id).classList.toggle("hidden");
    };

    w.toggleAllCheckboxes = function(checkbox) {
        var inputs = document.getElementsByName("user_id");
        for (var i = 0; i < inputs.length; ++i) {
            inputs[i].checked = checkbox.checked;
        }
    };

    w.submitForm = function(inputId, action) {
        var input = document.getElementById(inputId);
        input.value = action;
    };

    w.showPopup = function(popupId) {
        w.toggleHidden(popupId);
        w.toggleHidden("lightbox");
    };

    w.Password = {

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

})(django.jQuery, window, DAFO);