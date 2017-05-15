  function write_out(data) {
    $("#out").text(data.text);
    return false;
  }

  function return_process(data) {
    // $("#out").text(data.text);
    return_count = parseInt(data.return_val, 10);
    if (return_count >= 0) {
      update_list(data.wordlist);
      word_count = return_count;
    }
    else {
      // XXX: This is where we handle when the word count max is reached. XXX
      //alert(urlDone);
      // XXX: use replace for production
      // window.location.replace(urlDone);
      
      // XXX: Don't move ahead. We're testing this page. XXX
      // $(location).attr('href', urlDone)
      update_list(data.wordlist);
      word_count = return_count;
    }
    sim_msg = '';
    similarity = data.similarity;
    if (similarity != null) {
      sim_msg = '<p>The similarity was: </p> <p>' + similarity + '</p>';

      // $('#sim').html('<p>The similarity was: </p> <p>' + similarity + '</p>');
      // $('#out').append('<p><div>Your last word was: ' + last_word + '</div></p>');
    }

    sim_text = data.simtext;
    if (sim_text !== '') {
      sim_msg += ' <p>' + sim_text + '</p>';
    }

    $('#sim').html(sim_msg);
    // if (data.return_val == '0') {
      // update_list(data.wordlist);
      // word_count++;
    // }
    // if (word_count >= 20) {
      // XXX: This is where we handle when the word count max is reached. XXX
      // $('#out').append('<p><div>20 or more words entered.</div></p>');
      // window.location.replace("/survey");
    // }
    if (last_word !== '') {
      $('#out').html('<p>Your last word was: </p> <p>' + last_word + '</p>');
      // $('#out').append('<p><div>Your last word was: ' + last_word + '</div></p>');
      // $('#count').html('<p><div>You have entered ' + word_count + '/20 words.</div></p>');
      print_count(word_count);
    }
  }

  function print_count(word_count) {
    // $('#count').html('<p><div>You have entered ' + word_count + '/20 words.</div></p>');
  }

  function reset_words(data) {
    write_out(data);
    update_list(data.wordlist);
    word_count = 0;
    // $('#count').html('<p><div>You have entered ' + word_count + '/20 words.</div></p>');
    print_count(word_count);
  }

  function process() {
	end = new Date().getTime();
	duration = end - start;
    new_word = $("input[name='thought']").val();
    //$.post("{{ url_for('process_thoughts') }}", { 'thought': $("input[name='thought']").val() }, return_process, "json")
    $.post(urlProcess, { 'thought': new_word, 'duration': duration }, return_process, "json")
      .done(function () {
        // Reset the text box.
        $("input[name='thought']").val("");
        $("input[name='thought']").focus();
        start = new Date().getTime();
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
