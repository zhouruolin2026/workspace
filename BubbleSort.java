public class BubbleSort {
    
    // 冒泡排序算法
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            // 标记是否发生交换
            boolean swapped = false;
            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    // 交换
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            // 没发生交换说明已经有序，提前结束
            if (!swapped) break;
        }
    }
    
    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90};
        
        System.out.println("排序前: " + java.util.Arrays.toString(arr));
        bubbleSort(arr);
        System.out.println("排序后: " + java.util.Arrays.toString(arr));
    }
}
