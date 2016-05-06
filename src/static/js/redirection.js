function checkValidDomain(domain) {
  return /^(www\.)?[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/.test(domain);
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
    var domain = $(this).val();

    if (!checkValidDomain(domain)) {
      return;
    }

    if (!domain || domain.indexOf('www.') === 0) {
      $('label#altdomain').hide();
      return;
    }

    if (localDomain) {
      var ereg = new RegExp(localDomain + '$');
      if (domain.match(ereg) === null) {
        domain += '.' + localDomain;
      }
    }

    $('label#altdomain').show();
    $('label#altdomain strong').text('www.' + domain);
  });

  $('form[name=red] button.generate').click(function (e) {
    e.preventDefault();
    $('img.spinner-generate').show();
    $.ajax({
      type: 'POST',
      url: '/api/red/generate',
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        $('img.spinner-generate').hide();
        alert(data.message);
      },

      error: function (error) {
        $('img.spinner-generate').hide();
        alert('Error generating Ngnix configuration');
      },
    });
    return false;
  });

  $('form[name=red] button.add').click(function (e) {
    e.preventDefault();

    var domain = $('form[name=red] input[name=domain]').val();
    if (localDomain) {
      var ereg = new RegExp(localDomain + '$');
      if (domain.match(ereg) === null) {
        domain += '.' + localDomain;
      }
    }

    var url = $('form[name=red] input[name=url]').val();
    var altdomain = domain.indexOf('www.') !== 0 &&
                    $('form[name=red] label#altdomain input:checked').length === 1;

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

    $('img.spinner-add').show();
    $.ajax({
      type: 'POST',
      url: $('form[name=red]').attr('action'),
      data: JSON.stringify({ domain: domain, url: url, alt: altdomain }),
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        $('input[name=domain]').val('').focus();
        $('input[name=url]').val('');
        $('label#altdomain').hide();
        updateTable();
        $('img.spinner-add').hide();
      },

      error: function (error) {
        $('img.spinner-add').hide();
        alert(error.responseJSON.message);
      },
    });
  });

  function updateTable() {
    $('div.spinner').show();
    $.ajax({
      type: 'GET',
      url: '/api/red',
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        $('div.spinner').hide();
        redirections = data.rows.slice();
        $('table tbody').empty();
        for (var i in data.rows) {
          var row = data.rows[i];
          var narrowUrl = row.url;
          if (narrowUrl.length > 50) {
            narrowUrl = narrowUrl.substring(0, 50) + '...';
          }

          var className = i % 2 === 0 ? '' : 'pure-table-odd';
          $('table tbody').append(
            '<tr class="' + className + '">' +
            '<td>' + row.id + '</td>' +
            '<td><a href="http://' + row.domain + '">' + row.domain + '</a></td>' +
            '<td><a href="' + row.url + '" title="' + row.url + '">' + narrowUrl + '</a></td>' +
            '<td>' + row.date_added + '</td>' +
            '<td><button type="submit" data-id="' + row.id +
            '" class="pure-button pure-button-secondary del">' +
            '<img class="spinner-remove-' + row.id +
            '" src="/static/img/spinner-remove.gif" />' +
            ' Remove</button></td>' +
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
      var tr = $(this).closest('tr');
      var redId = $(this).data('id');

      $('img.spinner-remove-' + redId).show();

      $.ajax({
        type: 'DELETE',
        url: $('form[name=red]').attr('action'),
        data: JSON.stringify({ id: redId }),
        contentType: 'application/json;charset=UTF-8',
        success: function (data, status) {
          updateTable();
        },

        error: function (error) {
          $('img.spinner-remove-' + redId).hide();
          console.log('fail');
        },
      });
    });
  }

  updateTable();
});
