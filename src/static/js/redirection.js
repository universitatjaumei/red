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
    if (redirection.domain === red.domain) {
      duplicated = true;
    }
  });

  return duplicated;
}

$(document).ready(function () {

  var redirections;
  var localDomain;

  $.ajax({
    type: 'GET',
    url: '/api/red/local_domain',
    contentType: 'application/json;charset=UTF-8',
    success: function (data, status) {
      localDomain = data.domain;
      if (localDomain) {
        $('span.domain').html('.' + localDomain);
        $('span.domain').show();
      }
    },
  });

  $('form[name=red] input#domain').on('change', function (data) {
    var value = $(this).val();
    if (!value || value.indexOf('www.') === 0) {
      $('label#altdomain').hide();
      return;
    }

    if (localDomain) {
      value += '.' + localDomain;
    }

    $('label#altdomain').show();
    $('label#altdomain strong').text('www.' + value);
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

    var domain = $('form[name=red] input[name=domain]').val();
    if (localDomain) {
      domain += '.' + localDomain;
    }

    var url = $('form[name=red] input[name=url]').val();
    var altdomain = domain.indexOf('www.') !== 0 && $('form[name=red] label#altdomain input:checked').length === 1;

    if (!checkValidDomain(domain)) {
      alert('Invalid domain');
      return;
    }

    if (!checkValidURL(url)) {
      alert('Invalid URL');
      return;
    }

    if (checkDomainDuplicated(redirections, { domain: domain, url: url })) {
      alert('Duplicated redirection ' + domain);
      return;
    }

    if (altdomain &&
        domain.indexOf('www.') !== 0 &&
        checkDomainDuplicated(redirections, { domain: 'www.' + domain, url: url })) {
      alert('Duplicated redirection www.' + domain);
      return;
    }

    $.ajax({
      type: 'POST',
      url: $('form[name=red]').attr('action'),
      data: JSON.stringify({ domain: domain, url: url, alt: altdomain }),
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        $('input[name=domain]').val('').focus();
        $('input[name=url]').val('');
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
            '<td><a href="' + row.domain + '">' + row.domain + '</a></td>' +
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
