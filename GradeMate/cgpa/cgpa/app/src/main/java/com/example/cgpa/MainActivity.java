// MainActivity.java
package com.example.cgpa;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button itButton = findViewById(R.id.it_button);
        Button aidsButton = findViewById(R.id.aids_button);

        itButton.setOnClickListener(v -> openSemesterActivity("IT"));
        aidsButton.setOnClickListener(v -> openSemesterActivity("AIDS"));
    }

    private void openSemesterActivity(String department) {
        Intent intent = new Intent(MainActivity.this, SemesterActivity.class);
        intent.putExtra("department", department);
        startActivity(intent);
    }
}
