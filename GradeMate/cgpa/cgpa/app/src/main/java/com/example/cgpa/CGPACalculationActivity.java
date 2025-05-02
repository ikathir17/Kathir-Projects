// CGPACalculationActivity.java
package com.example.cgpa;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class CGPACalculationActivity extends AppCompatActivity {
    private EditText[] grades;
    private TextView resultText;
    private int numCourses;
    private String[] courseNames;
    private float[] credits;

    @SuppressLint("MissingInflatedId")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cgpa_calculation);

        resultText = findViewById(R.id.result_text);
        Button calculateButton = findViewById(R.id.calculate_button);
        LinearLayout courseContainer = findViewById(R.id.courseContainer);

        int semester = getIntent().getIntExtra("semester", 1);
        String department = getIntent().getStringExtra("department");

        configureCourses(department, semester);

        grades = new EditText[numCourses];
        for (int i = 0; i < numCourses; i++) {
            TextView courseText = new TextView(this);
            courseText.setText(courseNames[i]);
            courseContainer.addView(courseText);

            grades[i] = new EditText(this);
            grades[i].setHint("Enter Grade");
            courseContainer.addView(grades[i]);
        }

        calculateButton.setOnClickListener(v -> calculateCGPA());
    }

    private void configureCourses(String department, int semester) {
        if ((department.equals("IT") || department.equals("AIDS")) && semester == 1) {
            numCourses = 5;
            courseNames = new String[]{
                    "Linear Algebra and Calculus - 4 credits",
                    "Communication Skills in English Part 1 - 2 credits",
                    "BEEE - 3 credits",
                    "Physics - 3 credits",
                    "Python Programming - 3 credits"
            };
            credits = new float[]{4, 2, 3, 3, 3};
        } else if ((department.equals("IT") || department.equals("AIDS")) && semester == 2) {
            numCourses = 6;
            courseNames = new String[]{
                    "Applied Probability and Statistics - 4 credits",
                    "Communication Skills in English Part 2 - 3 credits",
                    "Chemistry - 3 credits",
                    "Engineering Graphics - 3 credits",
                    "C Programming - 3 credits",
                    "IT Essentials - 2 credits"
            };
            credits = new float[]{4, 3, 3, 3, 3, 2};
        }
    }

    private void calculateCGPA() {
        try {
            double totalGradePoints = 0;
            double totalCredits = 0;

            for (int i = 0; i < numCourses; i++) {
                double gradePoint = getGradePoint(grades[i].getText().toString());
                totalGradePoints += gradePoint * credits[i];
                totalCredits += credits[i];
            }

            double cgpa = totalGradePoints / totalCredits;
            resultText.setText("Your CGPA: " + String.format("%.2f", cgpa));

        } catch (Exception e) {
            Toast.makeText(CGPACalculationActivity.this, "Please enter valid grades!", Toast.LENGTH_SHORT).show();
        }
    }

    private double getGradePoint(String grade) {
        switch (grade.toUpperCase()) {
            case "O":
                return 10;
            case "A":
                return 9;
            case "B":
                return 8;
            case "C":
                return 7;
            case "D":
                return 6;
            case "FAIL":
                return 0;
            default:
                throw new IllegalArgumentException("Invalid grade entered");
        }
    }
}
