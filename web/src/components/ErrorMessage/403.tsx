import {Button,Result} from 'antd'
import {useNavigate} from 'react-router-dom'
import './index.less'


const NotAuth = () => {
    const navigate = useNavigate()
    const goHome = () => {
        navigate('/home')
    }

    return (
        <Result
            status='403'
            title='not auth'
            subTitle='Sorry, you are not authorized to access this page.'
            extra={
                <Button
                    type='primary'
                    onClick={goHome}
                    >Back Home</Button>
            }
        />
    )
}

export default NotAuth