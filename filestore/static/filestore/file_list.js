document.addEventListener('DOMContentLoaded', function() {
    var rootEl = document.documentElement;
    var num_files = document.querySelectorAll('.selected_files').length;
    var num_files_selected_spans = document.getElementsByClassName('num_files_selected');

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
                for (const selected_file of selected_files) {
                    selected_file.checked = true;
                }
            } else {
                for (const selected_file of selected_files) {
                    selected_file.checked = false;
                }
            }
            update_form();
        });
    }

    function update_form() {
        if (num_files > 0) {
            var checkedOne = Array.prototype.slice.call(selected_files).some(x => x.checked);
            var num_files_text = null;
            var num_files_selected = Array.prototype.slice.call(selected_files).filter(x => x.checked).length;
            if (checkedOne) {
                show_delete_modal_btn.removeAttribute('disabled');
                num_files_text = '&nbsp;(' + num_files_selected + ') file';
                if (num_files_selected > 1) {
                    num_files_text += 's';
                }
                if (num_files === num_files_selected) {
                    select_all.checked = true;
                }
            } else {
                show_delete_modal_btn.setAttribute('disabled', '');
                select_all.checked = false;
            }

            for (const span of num_files_selected_spans) {
                span.innerHTML = num_files_text;
            }
        }
    }

    var selected_files = document.querySelectorAll('.selected_files');
    for (const selected_file of selected_files) {
        selected_file.addEventListener('click', function() {
            update_form();
        });
    }
    update_form();
});
