document.addEventListener('DOMContentLoaded', function() {
    var rootEl = document.documentElement;
    var num_folders = document.querySelectorAll('.selected_folders').length;
    var num_folders_selected_spans = document.getElementsByClassName('num_folders_selected');

    var show_delete_modal_btn = document.getElementById('show_delete_modal_btn');
    if (show_delete_modal_btn) {
        show_delete_modal_btn.addEventListener('click', function() {
            var confirm_delete_modal = document.getElementById('confirm_delete_modal');
            rootEl.classList.add('is-clipped');
            confirm_delete_modal.classList.add('is-active');
        });
    }

    var cancel_delete_btn = document.getElementById('cancel_delete_btn');
    if (cancel_delete_btn) {
        cancel_delete_btn.addEventListener('click', function() {
            var confirm_delete_modal = document.getElementById('confirm_delete_modal');
            rootEl.classList.remove('is-clipped');
            confirm_delete_modal.classList.remove('is-active');
        });
    }

    var select_all = document.getElementById('select_all');
    if (select_all) {
        select_all.addEventListener('click', function() {
            if (select_all.checked) {
                for (const selected_folder of selected_folders) {
                    selected_folder.checked = true;
                }
            } else {
                for (const selected_folder of selected_folders) {
                    selected_folder.checked = false;
                }
            }
            update_form();
        });
    }

    function update_form() {
        if (num_folders > 0) {
            var checkedOne = select_all.checked || Array.prototype.slice.call(selected_folders).some(x => x.checked);
            var num_folders_text = null;
            var num_folders_selected = Array.prototype.slice.call(selected_folders).filter(x => x.checked).length;
            if (checkedOne) {
                show_delete_modal_btn.removeAttribute('disabled');
                num_folders_text = '&nbsp;(' + num_folders_selected + ') folder';
                if (num_folders_selected > 1) {
                    num_folders_text += 's';
                }
                if (num_folders === num_folders_selected) {
                    select_all.checked = true;
                }
            } else {
                show_delete_modal_btn.setAttribute('disabled', '');
                select_all.checked = false;
            }

            for (const span of num_folders_selected_spans) {
                span.innerHTML = num_folders_text;
            }
        }
    }

    var selected_folders = document.querySelectorAll('.selected_folders');
    for (const selected_folder of selected_folders) {
        selected_folder.addEventListener('click', function() {
            update_form();
        });
    }
    update_form();
});
