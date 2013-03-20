function DesiredColumn() {
	this.table = '';
	this.column = '';
	this.aggregate = '';
	this.selected = '';
}

function Filter(filterType) {
	this.type = filterType;
	this.boolType = '';
	this.filters = [];
	this.table = '';
	this.column = '';
	this.operator = '';
	this.value1 = '';
	this.value2 = '';
	this.aggregate = '';
}

function FilterList(type) {
	this.boolType = type;
	this.filters = [];
	this.selected = '';
}

var myApp = angular.module('myApp', ['ui']);
myApp.controller('QueryCtrl',function ($scope, $http) {
	$scope.items = ["One", "Two", "Three"];

    $scope.desiredcols = new Array();
    $scope.filters = new Array();
    $scope.limit = '';
    $scope.results = '';
    $scope.sql = '';
    $scope.erd = '';    
    $scope.rowcount = 10;
    $scope.distinct = true;
    
    $scope.aggOptions = ['COUNT', 'SUM', 'MIN', 'MAX', 'AVG', 'Clear'];
    $scope.filOptions = ['AND'];
    
    $scope.operators = [
    	{id: '=', text: '='}, 
		{id: '<', text: '<'}, 
		{id: '<=', text: '<='}, 
		{id: '>', text: '>'}, 
		{id: '>=', text: '>='},
		{id: '<>', text: '<>'}, 
		{id: 'between', text: 'Btw'}
    ];
    
    $scope.select2Options = {
    	minimumResultsForSearch:25
	  };
    
    $http.get('/databases').success(function(data) {
        $scope.databases = data;
    });
    
    $scope.changeSelection = function(o) {
    	o.selected = !o.selected;
    }
    
    $scope.toolClicked = function(tool) {
    	var cs = $scope.desiredcols;
		for ( var i = 0; i < cs.length; i++) {
			var sel = cs[i].selected;
	      if (sel === true) {
	      	if (tool === 'Clear') {
	      		cs[i].aggregate ='';
	      	}
	      	else {
	        	cs[i].aggregate=tool;
	        }
	      }
	    }  	
    }
    
    $scope.filterOptionClicked = function(filterOption) {
    	var fils = $scope.filters;
    	var firstSelected = -1;
    	var filsToCombine = [];
		for ( var i = 0; i < fils.length; i++) {
			var fil = fils[i];
			var sel = fil.selected;
			if (sel === true) { 
		      	/*Identify where the final result will be in the filters list*/
		      	if (firstSelected < 0) {
		      		firstSelected = i;
		      	}
		      	/*Start combining all the filters that are selected into a list*/
		      	filsToCombine.push(fil);
	      	}
		}
		
		/*Remove all but the first from the list*/
		for ( var i = 1; i < filsToCombine.length; i++) {
			$scope.removeFilter(filsToCombine[i]);						
	    }
	    
      	/*If the list is greater than 1, then create an AndFilter*/
      	if (filsToCombine.length > 1) {
  			af = new Filter('MANY');
  			af.boolType = filterOption;
  			for ( var i = 0; i < filsToCombine.length; i++) {
				af.filters.push(filsToCombine[i]);						
		    }
		    $scope.filters[firstSelected] = af;
      	} 	
    }
    
    $scope.updateSchema = function() {
    	var id = $scope.database;
    	$scope.schema = '';
    	$scope.typeOptions = [];
    	$scope.desiredcols = new Array();
    	$scope.filters = new Array();
    	
	    $http.get('/' + id + '/schema').success(function(data) {
	        $scope.schema = data;
	        $scope.typeOptions = [];
	        for (var tab in $scope.schema){        	
	        	$scope.typeOptions.push(tab);
	        }
	    });
    }

    $scope.addDesiredCol = function() {
        $scope.desiredcols.push(new DesiredColumn());
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
        $scope.filters.push(new Filter('ONE')); 
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
        var request = angular.toJson({
        	desiredcolumns: $scope.desiredcols,
        	filters: $scope.filters,
        	rowlimit: $scope.rowcount,
        	distinct: $scope.distinct        
        });
        
        var id = $scope.database;
        
        $http.post('/' + id + '/query', request).success(function(data) {
	        $scope.sql = data['sql'];
	        $scope.results = data['data'];
    	});
    };
});