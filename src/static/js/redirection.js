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

  var redirections = [];
  var localDomain;

  $('.typing').typing({
      stop: function (event, $elem) {
        updateTable(redirections, $elem.val());
      },
      delay: 400
  });

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

  $("#edit button.change-redirection").click(function(ev) {
    var id = $("#edit input.id").val();
    var redirect = $("#edit input.new-redirection").val();

    if (!checkValidURL(redirect)) {
      alert('Invalid redirect URL');
      return;
    }

    $('img.spinner-edit').show();

    $.ajax({
      type: 'PUT',
      url: '/api/red/' + id,
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({ id: id, redirect: redirect }),
      success: function (data, status) {
        $('img.spinner-edit').hide();
        if (data.status === 500) {
          return alert(data.message);
        }
        $.modal.close();
        refreshData();
      },

      error: function (error) {
        $('img.spinner-generate').hide();
        alert("Server error");
      },
    });
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
        var responseMessage = JSON.parse(error.responseText);
        alert(responseMessage.message);
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
        refreshData();
        $('img.spinner-add').hide();
      },

      error: function (error) {
        refreshData();
        $('img.spinner-add').hide();
        alert(error.responseJSON.message);
      },
    });
  });

  function updateTable(redirections, filter) {
    $('table tbody').empty();
    for (var i in redirections) {
      var row = redirections[i];
      var narrowUrl = row.url;
      if (narrowUrl.length > 45) {
        narrowUrl = narrowUrl.substring(0, 45) + '...';
      }

      var status_img = row.status ? "/static/img/status_ok.jpg" : "/static/img/status_error.png";
      var className = i % 2 === 0 ? '' : 'pure-table-odd';
      if (!row.status) {
        className = i % 2 === 0 ? 'redrow-even' : 'redrow-odd';
      }

      if (!filter || new RegExp(filter, 'i').test(row.domain)) {
        $('table tbody').append(
          '<tr class="' + className + '">' +
          '<td class="id"><img title="' + row.message + '" src="' + status_img +'" /></td>' +
          '<td class="domain"><a href="http://' + row.domain + '">' + row.domain + '</a></td>' +
          '<td><a href="#" class="openmodal"><img class="edit" src="/static/img/edit.png" /></a> <a data-id="' + row.id + '" class="redirect" href="' + row.url + '" title="' + row.url + '">' + narrowUrl + '</a></td>' +
          '<td class="date">' + row.date_added + '</td>' +
          '<td><button type="submit" data-id="' + row.id +
          '" class="pure-button pure-button-secondary del">' +
          '<img class="spinner-remove-' + row.id +
          '" src="/static/img/spinner-remove.gif" />' +
          ' Remove</button></td>' +
          '</tr>'
        );
      }
    }

    updateListeners();
  }

  function refreshData() {
    $('div.spinner').show();
    $.ajax({
      type: 'GET',
      url: '/api/red',
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        $('div.spinner').hide();
        redirections = data.rows.slice();
        updateTable(redirections);
      },

      error: function (error) {
        console.log('fail');
      },
    });
  }

  function updateListeners() {
    $('a.openmodal').click(function(ev) {
      var domain = $(this).parent().parent().children("td.domain").children("a").text();
      var redirect = $(this).parent().children("a.redirect").attr("title");
      var id = $(this).parent().children("a.redirect").data("id");
      ev.preventDefault();
      $("#edit strong.domain").text(domain);
      $("#edit strong.redirection").html(redirect);
      $("#edit input.id").val(id);
      $("#edit input.new-redirection").val('');
      $('#edit').modal();
    });

    $('table button.del').on('click', function (e) {
      e.preventDefault();
      var tr = $(this).closest('tr');
      var redId = $(this).data('id');

      $('img.spinner-remove-' + redId).show();

      $.ajax({
        type: 'DELETE',
        url: '/api/red/' + redId,
        contentType: 'application/json;charset=UTF-8',
        success: function (data, status) {
          refreshData();
        },

        error: function (error) {
          $('img.spinner-remove-' + redId).hide();
          console.log('fail');
        },
      });
    });
  }

  refreshData();
});
