package com.example.paythactivity;

import androidx.appcompat.app.AppCompatActivity;

import android.app.AlertDialog;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.Switch;
import android.widget.TextView;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import de.hdodenhof.circleimageview.CircleImageView;

public class MainActivity3 extends AppCompatActivity {
    FirebaseDatabase rti;
    DatabaseReference mfi, textRef;

    CircleImageView engineerImage;
    TextView engineerName;
    TextView timerValue;
    TextView counterValue;
    Switch motorSwitch;
    TextView fcEntryStatus;
    TextView fcExitStatus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main3);
        getSupportActionBar().hide();
        rti=FirebaseDatabase.getInstance();
        mfi = rti.getReference("plc");
        textRef = rti.getReference("plc");
       // View redDot = findViewById(R.id.redDot);
        timerValue = findViewById(R.id.timerValue);
        counterValue = findViewById(R.id.counterValue);
        motorSwitch = findViewById(R.id.motorSwitch);
        fcEntryStatus = findViewById(R.id.fcEntryStatus);
        fcExitStatus = findViewById(R.id.fcExitStatus);
        motorSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                mfi.child("motor").setValue(b);
            }
        });
        textRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot snapshot) {
                if (snapshot.exists()) {
                    timerValue.setText(snapshot.child("timer").getValue().toString());
                    counterValue.setText(snapshot.child("counter").getValue().toString());
                    String enterValue = snapshot.child("enter").getValue().toString();
                    String sortierValue = snapshot.child("sortier").getValue().toString();
                    fcEntryStatus.setText(enterValue);
                    fcExitStatus.setText(sortierValue);
        /*            if (enterValue.equals(sortierValue)) {
                        AlertDialog.Builder builder = new AlertDialog.Builder(MainActivity3.this);
                        builder.setTitle("تنبيه");
                        builder.setMessage("تم تطابق حالة الدخول والخروج!");
                        builder.setPositiveButton("حسناً", null);
                        builder.show();

                    }*/


                    if (enterValue.equalsIgnoreCase("ACTIVE")) {
                        fcEntryStatus.setTextColor(Color.parseColor("#0EAC9A")); // أخضر
                    } else {
                        fcEntryStatus.setTextColor(Color.parseColor("#D51616")); // أحمر
                    }

                    if (sortierValue.equalsIgnoreCase("ACTIVE")) {
                        fcExitStatus.setTextColor(Color.parseColor("#0EAC9A")); // أخضر
                    } else {
                        fcExitStatus.setTextColor(Color.parseColor("#D51616")); // أحمر
                    }
                }

            }

            @Override
            public void onCancelled(DatabaseError error) {

            }
        });

    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
    return  true;
    }
}
