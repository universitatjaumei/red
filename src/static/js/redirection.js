
function checkValidUJIDomain(domain) {
  if (/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9].uji.es$/.test(domain)) {
    return true;
  }

  return false;
}

function checkValidURL(url) {
  if (/^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/.test(url)) {
    return true;
  }

  return false;
}

function checkDomainDuplicated(redirections, red) {
  var duplicated = false;

  redirections.filter(function (redirection) {
    if (redirection.url === red.url || redirection.host === red.hostname) {
      duplicated = true;
    }
  });

  return duplicated;
}

$(document).ready(function () {

  var redirections;

  $('form[name=red] button.generate').click(function (e) {
    e.preventDefault();
    $.ajax({
      type: 'POST',
      url: '/api/red/generate',
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        alert(data.message);
      },

      error: function (error) {
        alert(error.responseJSON.message);
      },
    });
    return false;
  });

  $('form[name=red] button.add').click(function (e) {
    e.preventDefault();

    var hostname = $('form[name=red] input[name=hostname]').val();
    var url = $('form[name=red] input[name=url]').val();

    if (!checkValidUJIDomain(hostname)) {
      alert('Invalid hostname');
      return;
    }

    if (!checkValidURL(url)) {
      alert('Invalid URL');
      return;
    }

    if (checkDomainDuplicated(redirections, { hostname: hostname, url: url })) {
      alert('Duplicated redirection');
      return;
    }

    $.ajax({
      type: 'POST',
      url: $('form[name=red]').attr('action'),
      data: JSON.stringify({ hostname: hostname, url: url }),
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        updateTable();
      },

      error: function (error) {
        alert(error.responseJSON.message);
      },
    });
  });

  function updateTable() {
    $.ajax({
      type: 'GET',
      url: '/api/red',
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        redirections = data.rows.slice();
        $('table tbody').empty();
        for (var i in data.rows) {
          var row = data.rows[i];
          var className = i % 2 === 0 ? '' : 'pure-table-odd';
          $('table tbody').append(
            '<tr class="' + className + '">' +
            '<td>' + row.id + '</td>' +
            '<td><a href="' + row.host + '">' + row.host + '</a></td>' +
            '<td><a href="' + row.url + '">' + row.url + '</a></td>' +
            '<td>' + row['date_added'] + '</td>' +
            '<td><button type="submit" data-id="' + row.id + '" class="pure-button pure-button-secondary del">Remove</button></td>' +
            '</tr>'
          );
        }

        updateListeners();
      },

      error: function (error) {
        console.log('fail');
      },
    });
  }

  function updateListeners() {
    $('table button.del').on('click', function (e) {
      e.preventDefault();
      $(this).closest('tr').remove();
      var redId = $(this).data('id');

      $.ajax({
        type: 'DELETE',
        url: $('form[name=red]').attr('action'),
        data: JSON.stringify({ id: redId }),
        contentType: 'application/json;charset=UTF-8',
        success: function (data, status) {
          updateTable();
        },

        error: function (error) {
          console.log('fail');
        },
      });

      updateTable();
      return false;
    });
  }

  updateTable();
});
