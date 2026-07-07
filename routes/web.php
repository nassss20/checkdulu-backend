<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return response()->json(['status' => 'CheckDulu Backend is LIVE and healthy!']);
});