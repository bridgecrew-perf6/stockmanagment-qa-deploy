// Call the dataTables jQuery plugin
// $(document).ready(function() {
//   $('#dataTable').DataTable();
// });

$(document).ready( function() {
  $('#dataTable').DataTable( {
      dom: 'Bfrtip',
      buttons: [ {
          extend: 'excelHtml5',
          autoFilter: true,
          sheetName: 'Exported data'
      } ]
  } );
} );