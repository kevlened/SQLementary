
function QueryCtrl($scope, $http) {
    var desiredcols = $scope.desiredcols = new Array('');
    var filters = $scope.filters = new Array('');
    $scope.limit = '';
    $scope.results = '';
    $scope.sql = '';
    $scope.erd = '';

    $scope.addDesiredCol = function() {
        $scope.desiredcols.push({
          table: '',
          column: ''
        });
        $scope.$apply();        
        /*$('.selectpicker').selectpicker();*/
    };
    
    $scope.removeColumn = function( col ) {
        for ( var i = 0; i < desiredcols.length; i++) {
	      if (col === desiredcols[i]) {
	        desiredcols.splice(i, 1);
	        break;
	      }
	    }
    };
    
    $scope.addFilter = function() {
        $scope.filters.push({
          table: '',
          column: '',
          operator: '',
          value1: '',
          value2: ''
        });
        $scope.$apply();    
        /*$('.selectpicker').selectpicker();*/
    };
    
    $scope.removeFilter = function( fil ) {
        for ( var i = 0; i < filters.length; i++) {
	      if (fil === filters[i]) {
	        filters.splice(i, 1);
	        break;
	      }
	    }
    };

    $scope.fetchErd = function() {
        $http.get('/erd/sample1').success(function(data) {
	        $scope.erd = data;
    	});
    };
    
    $scope.fetchQueryDataSQL = function() {
        $http.get('/query/sample1').success(function(data) {
	        $scope.temp = data;
	        $scope.results = $scope.temp.results;
	        $scope.sql = $scope.temp.sql;
    	});
    };
};