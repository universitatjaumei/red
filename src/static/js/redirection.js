
function checkValidDomain(domain) {
  if (/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/.test(domain)) {
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
    if (redirection.host === red.hostname) {
      duplicated = true;
    }
  });

  return duplicated;
}

$(document).ready(function () {

  var redirections;

  $('form[name=red] input#hostname').on('change', function (data) {
    var value = $(this).val();
    if (!value || value.indexOf('www.') === 0) {
      $('label#althostname').hide();
      return;
    }

    $('label#althostname').show();
    $('label#althostname strong').text('www.' + value);
  });

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
    var althostname = $('form[name=red] label#althostname input').val();

    if (!checkValidDomain(hostname)) {
      alert('Invalid hostname');
      return;
    }

    if (!checkValidURL(url)) {
      alert('Invalid URL');
      return;
    }

    if (checkDomainDuplicated(redirections, { hostname: hostname, url: url })) {
      alert('Duplicated redirection ' + hostname);
      return;
    }

    if (althostname === 'on' &&
        hostname.indexOf('www.') !== 0 &&
        checkDomainDuplicated(redirections, { hostname: 'www.' + hostname, url: url })) {
      alert('Duplicated redirection www.' + hostname);
      return;
    }

    $.ajax({
      type: 'POST',
      url: $('form[name=red]').attr('action'),
      data: JSON.stringify({ hostname: hostname, url: url, alt: althostname }),
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
