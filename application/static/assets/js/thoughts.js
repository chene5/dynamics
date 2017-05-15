  function write_out(data) {
    $("#out").text(data.text);
    return false;
  }

  function return_process(data) {
    $("#out").text(data.text);
    if (data.return_val == '0') {
      update_list(data.wordlist);
    }
    if (last_word !== '') {
      $('#out').append('<p><div>Your last word was: ' + last_word + '</div></p>');
    }
  }

  function reset_words(data) {
    write_out(data);
    update_list(data.wordlist);
  }

  function process() {
    new_word = $("input[name='thought']").val();
    //$.post("{{ url_for('process_thoughts') }}", { 'thought': $("input[name='thought']").val() }, return_process, "json")
    $.post(urlProcess, { 'thought': new_word }, return_process, "json")
      .done(function () {
        // Reset the text box.
        $("input[name='thought']").val("");
        $("input[name='thought']").focus()
      });
  }

  function reset_thoughts() {
    $.post(urlReset, { 'reset': 'reset' }, reset_words, "json")
      .done(function () {
        // Reset the text box.
        $("input[name='thought']").val("");
        $("input[name='thought']").focus()
        // Reset the word list.
        word_list = [];
      });
  }

  function save_words() {
    $.post(urlSave, { 'save': 'save' }, write_out, "json")
      .done(function () {
        // Reset the text box.
        $("input[name='thought']").val('');
        $("input[name='thought']").focus();
      });
  }

  function update_list(returned_words) {
    // Clear the existing list
    $('#previouswords .list-group li').remove();

    $.each(returned_words, function (index, word) {
      if (index == 0) {
        $('#previouswords .list-group').append('<li class="list-group-item active">' + word + '</li>')
      } else {
        $('#previouswords .list-group').append('<li class="list-group-item">' + word + '</li>')
      }
    });

    // $('#word-box').append('<div>' + new_word + '</div>');
    // $("#word-box").scrollTop($("#word-box")[0].scrollHeight);

    word_list.push(new_word);
    last_word = new_word;
  }
