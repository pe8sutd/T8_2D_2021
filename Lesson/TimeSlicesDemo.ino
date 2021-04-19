#include <MsTimer2.h>
#define TASKS_NUM 2
typedef struct _TASK_COMPONENTS
{
  uint8_t Run;  // 1:Task are ready to run
  uint8_t Timer;  // Current Time
  uint8_t ItvTime;  // Task run interval
  void (*TaskHook)(void); // The pointer to the task function to run
} TASK_COMPONENTS; // Task structure Definition 

void TaskRemarks(void);
void TaskProcess(void);
void Task1(void);
void Task2(void);

static TASK_COMPONENTS TaskComps[]={
  {0,100,100,Task1},
  {0,50,50,Task2}
};

void Task1(void)
{
  static int counter=0;
  Serial.print(counter++);
  Serial.write("-Task1\n");
}

void Task2(void)
{
  static int counter=0;
  Serial.print(counter++);
  Serial.write("-Task2\n");
}

void TaskRemarks(){
  uint8_t i;
  for (i=0;i<TASKS_NUM;i++){
    if (TaskComps[i].Timer)
    {
      TaskComps[i].Timer--;
//      Serial.write("Remark Running\n");
      if (TaskComps[i].Timer == 0){
        TaskComps[i].Timer = TaskComps[i].ItvTime;
        TaskComps[i].Run = 1;
      }
    }
  }
}

void TaskProcess(void){
  uint8_t i;
  for(i=0; i< TASKS_NUM; i++){
    if(TaskComps[i].Run){
//      Serial.write("Processing Running\n");
      TaskComps[i].TaskHook();
      TaskComps[i].Run = 0;
    }
  }
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  while (!Serial);
  MsTimer2::set(50,TaskRemarks);
}

void loop() {
  // put your main code here, to run repeatedly:
//Serial.available();
  MsTimer2::start();
  Serial.write("begin\n");
  while(1)
  {
      TaskProcess();
  }
}
