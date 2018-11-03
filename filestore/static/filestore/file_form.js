document.addEventListener('DOMContentLoaded', function() {
    var filename_div = document.getElementById('filename');
    document.getElementById("file_obj").onchange = function() {
        let f_array = this.value.split('\\');
        let filename = f_array[f_array.length - 1];
        let filesize = this.files[0].size;
        let filesize_kib = Math.round((parseInt(filesize) / 1024) * 100) / 100;
        filename_div.innerHTML = filename + " (" + filesize_kib + " KiB)";
    };
});
