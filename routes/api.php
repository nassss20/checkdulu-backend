<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ScanController;

Route::any('/scan-url', [App\Http\Controllers\ScanController::class, 'scanUrl']);