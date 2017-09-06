var DAFO = window.DAFO || {};

(function($, w, DAFO) {

    // Close the dropdown if the user clicks outside of it
    w.onclick = function(event) {
        if (event.target.closest('.dropbtn') === null &&
            event.target.closest('.search-term') === null) {
            closeDropDowns();
        }
        if (event.target.id === "lightbox") {
            closePopups();
        }
    };

    w.closeElementsByClassName = function(className) {
        var elements = document.getElementsByClassName(className);
        var i;
        for (i = 0; i < elements.length; i++) {
            var element = elements[i];
            if (element.classList.contains('show')) {
                element.classList.remove('show');
            }
        }
    };

    w.closeDropDowns = function() {
        closeElementsByClassName("dropdown-content");
    };

    w.closePopups = function() {
        toggleShow("lightbox");
        closeElementsByClassName("popup");
    };

    w.onkeydown = function(evt) {
        evt = evt || window.event;
        // Escape
        if (evt.keyCode === 27) {
            closePopups();
        }
    };

    /* When the user clicks on the button,
    toggle between hiding and showing the dropdown content */
    w.toggleShow = function(id) {
        document.getElementById(id).classList.toggle("show");
    };

    w.showPopup = function(popupId) {
        toggleShow(popupId);
        toggleShow("lightbox");
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
        input.closest('form').submit();
    };


    w.newPassword = function() {
        var new_pw = Password.generate(16);
        document.getElementById("id_password").value = new_pw;
        document.getElementById("password_display").innerHTML = new_pw;
    };

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
        }
    };


    $(document).ready(function() {

        $(".search-term").on("change paste keyup focus", function () {
            var search_term = $(this).val();
            var id = this.id;

            var search_body = $('.' + id + '_body');

            search_body.html('').load(
                "/ajax/" + id + "/?search_term=" + search_term
            );
            if(search_body !== "") {
                closeDropDowns();
                search_body.addClass("show");
            }

        });
    });

})(django.jQuery, window, DAFO);