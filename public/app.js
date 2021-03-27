$(document).ready(function() {
  var c = 0;
  $("#pageset-add-btn").click(function(){
      var htmlString = `
      <fieldset id="pageset-field-${c}">
          <label for="pageset-${c}-no">Nomor:</label>
          <input type="text" min="1" name="pageset-${c}-no" id="pageset-${c}-no" required>
          <label for="pageset-${c}-hal">Jumlah Halaman:</label>
          <input type="number" min="1" name="pageset-${c}-hal" id="pageset-${c}-hal" required>
          <button type="button" id="pageset-del-btn-${c}" data-index="${c}">Hapus</button>
      </fieldset>
      `;
      $("#pageset").append(htmlString);
      $(`#pageset-del-btn-${c}`).click(function(){
          var idx = $(this).data("index");
          $(`#pageset-field-${idx}`).remove();
      })
      c++;
  });
  $("#folder").change(function(){
    console.log($(this).val())
    if ($(this).val() == "custom"){
      $("#folder-custom").show();
    } else {
      $("#folder-custom").hide();
    }
  });
});
