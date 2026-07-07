<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('signatures', function (Blueprint $table) {
            $table->id();
            $table->string('hash_md5', 32)->unique(); 
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('signatures');
    }
};