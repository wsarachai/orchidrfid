angular.module('OrchidRFIDApp', [])
.controller('MainController',
	function($rootScope, $scope, $http, $timeout) {
	
	disabled = true;

	$rootScope.title = 'Orchid RFID Applications';
	$scope.isDataPresent = function() {
		return disabled;
	};
	$scope.saveClicked = function() {
    $http({
      url: '/' +
      		 $scope.trunk + '/' +
      		 $scope.branch + '/' +
      		 $scope.day + '/' +
      		 $scope.month + '/' +
      		 $scope.year1 + '/' +
      		 $scope.year2 + '/' +
      		 'save',
      method: "POST"
    })
    .then(function(response) {
      alert("success")
    }, 
    function(response) { // optional
      // failed
    });
	};
	
	$scope.trunk = '';
	$scope.branch = '';
	$scope.day = '';
	$scope.month = '';
	$scope.year1 = '';
	$scope.year2 = '';
	
  var timer = function() {
  	$http.get('/cards-status').then(function (response) {
			if (response.data.status) {
				if (disabled) {
  				disabled = false;
  				data = response.data.data
  				$scope.trunk = data[2];
	        $scope.branch = data[3];
	        $scope.day = data[4];
	        $scope.month = data[5];
	        $scope.year1 = data[6];
	        $scope.year2 = data[7];
  			}
			}
			else {
  			disabled = true;
  			$scope.trunk = '';
  			$scope.trunk = '';
	      $scope.branch = '';
	      $scope.day = '';
	      $scope.month = '';
	      $scope.year1 = '';
	      $scope.year2 = '';
			}
		}, function (error) {
			
		});
    $timeout(timer, 1000);
  }
  
  $timeout(timer, 1000);  
        
});