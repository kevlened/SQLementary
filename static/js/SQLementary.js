
function QueryCtrl($scope, $http) {
    $scope.desiredcols = new Array();
    $scope.filters = new Array();
    $scope.limit = '';
    $scope.results = '';
    $scope.sql = '';
    $scope.erd = '';       
    
    $http.get('/sample1/schema').success(function(data) {
        $scope.schema = data;
        $scope.typeOptions = [];
        for (var tab in $scope.schema){        	
        	$scope.typeOptions.push(tab);
        }
    });

    $scope.addDesiredCol = function() {
        $scope.desiredcols.push({
          table: '',
          column: ''
        });        
        /*$('.selectpicker').selectpicker();*/
    };
    
    $scope.removeColumn = function( col ) {
    	var desiredcols = $scope.desiredcols;
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
        /*$('.selectpicker').selectpicker();*/
    };
    
    $scope.removeFilter = function( fil ) {
    	var filters = $scope.filters;
        for ( var i = 0; i < filters.length; i++) {
	      if (fil === filters[i]) {
	        filters.splice(i, 1);
	        break;
	      }
	    }
    };

    $scope.fetchErd = function() {
        $http.get('/sample1/erd').success(function(data) {
	        $scope.erd = data;
    	});
    };
    
    $scope.fetchQueryDataSQL = function() {    
        var request = angular.toJson({desiredcolumns: $scope.desiredcols, filters: $scope.filters});
		/*$http({
            method: 'POST',
            url: '/sample1/query',
            data: request,
            headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            transformRequest: transform
        });*/
        $http.post('/sample1/query', request).success(function(data) {
	        $scope.sql = data['sql'];
	        $scope.results = data['data'];
    	});
    };
    
    var transform = function(data){
        return $.param(data);
    }
};