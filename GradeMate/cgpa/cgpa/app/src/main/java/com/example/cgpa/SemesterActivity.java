// SemesterActivity.java
package com.example.cgpa;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class SemesterActivity extends AppCompatActivity {
    private String department;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_semester);

        department = getIntent().getStringExtra("department");

        Button semester1Button = findViewById(R.id.semester1_button);
        Button semester2Button = findViewById(R.id.semester2_button);

        semester1Button.setOnClickListener(v -> openCGPACalculationActivity(1));
        semester2Button.setOnClickListener(v -> openCGPACalculationActivity(2));
    }

    private void openCGPACalculationActivity(int semester) {
        Intent intent = new Intent(SemesterActivity.this, CGPACalculationActivity.class);
        intent.putExtra("semester", semester);
        intent.putExtra("department", department);
        startActivity(intent);
    }
}
